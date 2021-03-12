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


# Need a way to delete non-published files
# Have copy/render methods return a list of Path objects
# Then can delete files which aren't in the list?
# set([p for p in request.renderpath.glob('**/*') if p.is_file()])
# https://stackoverflow.com/a/25675649
# https://stackoverflow.com/a/54216885

# create class, install class on request obj in mimir/__init__ instead of path obj


class Renderer(object):
    def __init__(self, request):
        self.render_path = pathlib.Path(request.registry.settings["render.location"])


def write_html(path, contents):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def write_feed(path, feed):
    path.parent.mkdir(parents=True, exist_ok=True)
    feed.write(path.open("w", encoding="utf-8"), "utf-8")


def copy_static_files(request):
    output = set()
    static_dest = request.renderpath / "static"
    static_dest.mkdir(parents=True, exist_ok=True)
    filenames = pkg_resources.resource_listdir("mimir", "render/static")
    for filename in filenames:
        outpath = static_dest / filename
        with outpath.open(mode="wb") as out:
            copyfileobj(
                pkg_resources.resource_stream(
                    "mimir", "/".join(["render/static", filename])
                ),
                out,
            )
        output.add(outpath)
    return output


def render_toc(request):
    site_title = request.registry.settings["render.site_title"]
    contact_email = request.registry.settings["render.contact_email"]
    writeups = (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts))
        .filter_by(published=True)
        .order_by(Writeup.title.collate("writeuptitle").asc(), Writeup.id.asc())
        .all()
    )

    content = pyramid.renderers.render(
        "mimir:render/toc.mako",
        {
            "writeups": writeups,
            "site_title": site_title,
            "contact_email": contact_email,
        },
        request=request,
    )

    outpath = request.renderpath / "index.html"
    write_html(outpath, content)
    return set([outpath])


def make_changelog_batch(request):
    generic_entries = (
        request.db_session.query(ChangeLogGenericEntry)
        .filter_by(batch=None)
        .order_by(ChangeLogGenericEntry.created_at.asc())
        .all()
    )
    writeup_entries = (
        request.db_session.query(ChangeLogWriteupEntry)
        .filter_by(batch=None)
        .order_by(ChangeLogWriteupEntry.created_at.asc())
        .all()
    )
    if len(generic_entries) == 0 and len(writeup_entries) == 0:
        return None
    batch = ChangeLogBatch()
    request.db_session.add(batch)
    for entry in generic_entries + writeup_entries:
        entry.batch = batch
    request.db_session.flush()
    return batch


def render_feed(request, generator, filename, batches):
    feed_title = "{} Recent Changes".format(
        request.registry.settings["render.site_title"]
    )
    description = pyramid.renderers.render(
        "mimir:render/toc#site_description.mako", {}, request=request
    ).strip()

    feed = generator(
        title=feed_title,
        link=request.route_url("rendered_toc"),
        language="en",
        description=description,
    )
    for batch in batches:
        batch_html = pyramid.renderers.render(
            "mimir:render/changelog#batch_feed_html.mako",
            {"batch": batch},
            request=request,
        ).strip()
        feed.add_item(
            title=format_datetime(batch.created_at, request.display_timezone),
            link=request.route_url("rendered_changelist", _anchor=batch.id.base62),
            unique_id=batch.id.base62,
            pubdate=batch.created_at,
            description=batch_html,
        )
    outpath = request.renderpath / "changes" / filename
    write_feed(outpath, feed)
    return outpath


def render_changelog(request):
    site_title = request.registry.settings["render.site_title"]
    contact_email = request.registry.settings["render.contact_email"]
    batches = (
        request.db_session.query(ChangeLogBatch)
        .order_by(ChangeLogBatch.id.desc())
        .limit(20)
        .all()
    )
    content = pyramid.renderers.render(
        "mimir:render/changelog.mako",
        {"batches": batches, "site_title": site_title, "contact_email": contact_email},
        request=request,
    )

    outpath_html = request.renderpath / "changes" / "index.html"
    write_html(outpath_html, content)

    outpath_rss = render_feed(request, feedgenerator.Rss201rev2Feed, "rss.xml", batches)
    outpath_atom = render_feed(request, feedgenerator.Atom1Feed, "atom.xml", batches)
    outpath_json = render_feed(request, JSONFeed, "feed.json", batches)

    return set([outpath_html, outpath_rss, outpath_atom, outpath_json])


def render_writeup(request, writeup):
    site_title = request.registry.settings["render.site_title"]
    contact_email = request.registry.settings["render.contact_email"]
    content = pyramid.renderers.render(
        "mimir:render/writeup.mako",
        {"writeup": writeup, "site_title": site_title, "contact_email": contact_email},
        request=request,
    )

    outpath = (
        request.renderpath / writeup.author_slug / writeup.writeup_slug / "index.html"
    )
    write_html(outpath, content)
    return set([outpath])


def render_changed(request):
    output = set()
    batch = make_changelog_batch(request)
    if batch is None:
        return output

    output.update(copy_static_files(request))
    output.update(render_toc(request))

    rendered_writeups = set()
    for writeup_entry in batch.writeup_entries:
        writeup = writeup_entry.writeup_post.writeup
        if writeup.id in rendered_writeups:
            continue
        output.update(render_writeup(request, writeup))
        rendered_writeups.add(writeup.id)

    output.update(render_changelog(request))
    return output


def render_all(request):
    make_changelog_batch(request)
    output = set()
    output.update(copy_static_files(request))
    output.update(render_toc(request))
    output.update(render_changelog(request))
    for writeup in (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts).joinedload(WriteupPost.active_version))
        .filter_by(published=True)
    ):
        output.update(render_writeup(request, writeup))
    output.update(render_changelog(request))
    return output
