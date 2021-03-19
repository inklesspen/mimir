import hashlib
import pathlib
from shutil import copyfileobj

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
        self.render_path = pathlib.Path(request.registry.settings["render.location"])
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

    def render_changed(self):
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

    def render_all(self):
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
