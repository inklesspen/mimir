from shutil import copyfileobj

import pkg_resources
import pyramid.renderers
from sqlalchemy.orm import joinedload

from ..models import Writeup, WriteupPost


def write_html(path, contents):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def copy_static_files(request):
    static_dest = request.renderpath / "static"
    static_dest.mkdir(parents=True, exist_ok=True)
    filenames = pkg_resources.resource_listdir("mimir", "render/static")
    for filename in filenames:
        with (static_dest / filename).open(mode="wb") as out:
            copyfileobj(
                pkg_resources.resource_stream(
                    "mimir", "/".join(["render/static", filename])
                ),
                out,
            )


def render_toc(request):
    writeups = (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts))
        .filter_by(published=True)
        .order_by(Writeup.title.collate("writeuptitle").asc(), Writeup.id.asc())
        .all()
    )

    output = pyramid.renderers.render(
        "mimir:render/toc.mako", {"writeups": writeups}, request=request
    )

    write_html(request.renderpath / "index.html", output)


def render_writeup(request, writeup):
    output = pyramid.renderers.render(
        "mimir:render/writeup.mako", {"writeup": writeup}, request=request
    )

    write_html(
        request.renderpath / writeup.author_slug / writeup.writeup_slug / "index.html",
        output,
    )


def render_all(request):
    copy_static_files(request)
    render_toc(request)
    for writeup in (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts).joinedload(WriteupPost.active_version))
        .filter_by(published=True)
    ):
        render_writeup(request, writeup)
