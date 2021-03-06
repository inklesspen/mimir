import dataclasses
from filecmp import dircmp
import hashlib
import os
import pathlib
from shutil import copy2, copyfileobj, copytree, rmtree

import feedgenerator
from jsonfeed import JSONFeed
import pkg_resources
import pyramid.renderers
from sqlalchemy.orm import joinedload

from ..models import (
    ChangeLogBatch,
    ChangeLogGenericEntry,
    ChangeLogWriteupEntry,
    Writeup,
    WriteupPost,
)
from ..util import format_datetime


def ensure_path(path):
    path.mkdir(parents=True, exist_ok=True)


def hash_file(filelike):
    h = hashlib.sha256()
    while chunk := filelike.read(4096):
        h.update(chunk)
    return h.hexdigest()


class Renderer(object):
    def __init__(self, request):
        # ideally we wouldn't need to keep this, but renderers use it
        self.request = request
        self.db_session = request.db_session
        self.render_path = pathlib.Path(
            request.registry.settings["render.build_location"]
        )
        self.deploy_path = pathlib.Path(
            request.registry.settings["render.serve_location"]
        )
        self.site_title = request.registry.settings["render.site_title"]
        self.contact_email = request.registry.settings["render.contact_email"]

        self.static_map = {}

    @staticmethod
    def write_html(path, contents):
        ensure_path(path.parent)
        path.write_text(contents, encoding="utf-8")

    def _static_file_route(self, filename):
        return self.static_map[filename]

    def _copy_static_files(self):
        static_dest = self.render_path / "static"
        ensure_path(static_dest)
        filenames = pkg_resources.resource_listdir("mimir", "render/static")
        for filename in filenames:
            resource_name = ["mimir", "/".join(["render/static", filename])]
            filename_parts = filename.split(".", 1)
            filehash = hash_file(pkg_resources.resource_stream(*resource_name))
            outfilename = "{}.{}.{}".format(
                filename_parts[0], filehash, filename_parts[1]
            )
            outpath = static_dest / outfilename
            with outpath.open(mode="wb") as out:
                copyfileobj(
                    pkg_resources.resource_stream(*resource_name),
                    out,
                )
            self.static_map[filename] = self.request.route_path(
                "rendered_static_file", filename=outfilename
            )

    def _render_template(self, template, **data):
        data["site_title"] = self.site_title
        data["contact_email"] = self.contact_email
        data["static_file_route"] = self._static_file_route

        return pyramid.renderers.render(template, data, request=self.request).strip()

    def _render_toc(self):
        writeups = (
            self.db_session.query(Writeup)
            .options(joinedload(Writeup.posts))
            .filter_by(published=True)
            .order_by(Writeup.title.collate("writeuptitle").asc(), Writeup.id.asc())
            .all()
        )

        content = self._render_template("mimir:render/toc.mako", writeups=writeups)

        outpath = self.render_path / "index.html"
        self.write_html(outpath, content)

    def _render_writeup(self, writeup):
        content = self._render_template("mimir:render/writeup.mako", writeup=writeup)

        outpath = (
            self.render_path / writeup.author_slug / writeup.writeup_slug / "index.html"
        )
        self.write_html(outpath, content)

    def _render_feed(self, generator, filename, batches):
        feed_title = "{} Recent Changes".format(self.site_title)
        description = self._render_template("mimir:render/toc#site_description.mako")

        feed = generator(
            title=feed_title,
            link=self.request.route_url("rendered_toc"),
            language="en",
            description=description,
        )
        for batch in batches:
            batch_html = self._render_template(
                "mimir:render/changelog#batch_feed_html.mako", batch=batch
            )
            feed.add_item(
                title=format_datetime(batch.created_at, self.request.display_timezone),
                link=self.request.route_url(
                    "rendered_changelist", _anchor=batch.id.base62
                ),
                unique_id=batch.id.base62,
                pubdate=batch.created_at,
                description=batch_html,
            )
        outpath = self.render_path / "changes" / filename
        ensure_path(outpath.parent)
        feed.write(outpath.open("w", encoding="utf-8"), "utf-8")

    def _make_changelog_batch(self):
        generic_entries = (
            self.db_session.query(ChangeLogGenericEntry)
            .filter_by(batch=None)
            .order_by(ChangeLogGenericEntry.created_at.asc())
            .all()
        )
        writeup_entries = (
            self.db_session.query(ChangeLogWriteupEntry)
            .filter_by(batch=None)
            .order_by(ChangeLogWriteupEntry.created_at.asc())
            .all()
        )
        if len(generic_entries) == 0 and len(writeup_entries) == 0:
            return None
        batch = ChangeLogBatch()
        self.db_session.add(batch)
        for entry in generic_entries + writeup_entries:
            entry.batch = batch
        self.db_session.flush()
        return batch

    def _render_changelog(self):
        batches = (
            self.db_session.query(ChangeLogBatch)
            .order_by(ChangeLogBatch.id.desc())
            .limit(20)
            .all()
        )
        content = self._render_template("mimir:render/changelog.mako", batches=batches)

        outpath_html = self.render_path / "changes" / "index.html"
        self.write_html(outpath_html, content)

        self._render_feed(feedgenerator.Rss201rev2Feed, "rss.xml", batches)
        self._render_feed(feedgenerator.Atom1Feed, "atom.xml", batches)
        self._render_feed(JSONFeed, "feed.json", batches)

    def _deploy(self):
        Deployer(self.render_path, self.deploy_path).perform()

    def render_changed(self):
        ensure_path(self.deploy_path)
        ensure_path(self.render_path)
        batch = self._make_changelog_batch()
        if batch is None:
            return

        self._copy_static_files()
        self._render_toc()

        rendered_writeups = set()
        for writeup_entry in batch.writeup_entries:
            writeup = writeup_entry.writeup_post.writeup
            if writeup.id in rendered_writeups or not writeup.published:
                continue
            self._render_writeup(writeup)

        self._render_changelog()
        self._deploy()

    def render_all(self):
        rmtree(self.render_path)
        ensure_path(self.deploy_path)
        ensure_path(self.render_path)
        self._make_changelog_batch()
        self._copy_static_files()
        self._render_toc()
        for writeup in (
            self.db_session.query(Writeup)
            .options(joinedload(Writeup.posts).joinedload(WriteupPost.active_version))
            .filter_by(published=True)
        ):
            self._render_writeup(writeup)
        self._render_changelog()
        self._deploy()


@dataclasses.dataclass
class Deployer(object):
    src_dir: pathlib.Path
    dest_dir: pathlib.Path

    to_add: set[pathlib.PurePath] = dataclasses.field(
        default_factory=set, init=False, repr=False, compare=False
    )
    to_update: set[pathlib.PurePath] = dataclasses.field(
        default_factory=set, init=False, repr=False, compare=False
    )
    to_remove: set[pathlib.PurePath] = dataclasses.field(
        default_factory=set, init=False, repr=False, compare=False
    )

    def _analyze(
        self,
        left_dir: pathlib.Path,
        right_dir: pathlib.Path,
        left_prefix: pathlib.PurePath,
        right_prefix: pathlib.PurePath,
    ):
        d = dircmp(left_dir, right_dir)
        for name in d.left_only:
            self.to_add.add(left_prefix / name)
        for name in d.right_only:
            self.to_remove.add(right_prefix / name)
        for name in d.diff_files:
            self.to_update.add(left_prefix / name)
        for sub in d.common_dirs:
            self._analyze(
                left_dir / sub, right_dir / sub, left_prefix / sub, right_prefix / sub
            )

    def analyze(self):
        self._analyze(
            self.src_dir, self.dest_dir, pathlib.PurePath(""), pathlib.PurePath("")
        )

    def _copy(self, paths: set[pathlib.PurePath]):
        for path in paths:
            src_path = self.src_dir / path
            dest_path = self.dest_dir / path
            if src_path.is_dir():
                # ensure_path(dest_path)
                copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                copy2(src_path, dest_path)

    def _remove(self, paths: set[pathlib.PurePath]):
        for path in paths:
            dest_path = self.dest_dir / path
            if dest_path.is_dir():
                rmtree(dest_path)
            else:
                os.remove(dest_path)

    def perform(self):
        # order matters! added files first, then modified files, then deleted files
        self.analyze()

        # print("Add: ", self.to_add)
        # print("Update: ", self.to_update)
        # print("Remove: ", self.to_remove)

        self._copy(self.to_add)
        self._copy(self.to_update)
        self._remove(self.to_remove)
