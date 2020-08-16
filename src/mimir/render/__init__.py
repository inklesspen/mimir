import pathlib
from shutil import copyfileobj

import pkg_resources
import pyramid.renderers
from sqlalchemy.orm import joinedload

from ..models import Writeup, WriteupPost


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
    writeups = (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts))
        .filter_by(published=True)
        .order_by(Writeup.title.collate("writeuptitle").asc(), Writeup.id.asc())
        .all()
    )

    content = pyramid.renderers.render(
        "mimir:render/toc.mako", {"writeups": writeups}, request=request
    )

    outpath = request.renderpath / "index.html"
    write_html(outpath, content)
    return set([outpath])


def render_writeup(request, writeup):
    content = pyramid.renderers.render(
        "mimir:render/writeup.mako", {"writeup": writeup}, request=request
    )

    outpath = (
        request.renderpath / writeup.author_slug / writeup.writeup_slug / "index.html"
    )
    write_html(outpath, content)
    return set([outpath])


def render_all(request):
    output = set()
    output.update(copy_static_files(request))
    output.update(render_toc(request))
    for writeup in (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts).joinedload(WriteupPost.active_version))
        .filter_by(published=True)
    ):
        output.update(render_writeup(request, writeup))
    return output
