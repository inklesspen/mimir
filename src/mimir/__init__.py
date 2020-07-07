import pathlib

import hashfs
from pyramid.config import Configurator


def request_hashfs(request):
    path = request.registry.settings["hashfs.location"]
    fs = hashfs.HashFS(path, depth=2, width=3, algorithm="sha256")
    return fs


def request_renderpath(request):
    return pathlib.Path(request.registry.settings["render.location"])


def admin_views(config):
    config.add_static_view("static", "static", cache_max_age=3600)
    config.include(".views")


def static_routes(config):
    config.add_route("writeup_image", "/images/{filename}", static=True)
    config.add_route("rendered_toc", "/", static=True)
    config.add_route("rendered_static_file", "/static/{filename}", static=True)
    config.add_route("rendered_writeup", "/{author_slug}/{writeup_slug}/", static=True)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.add_request_method(request_hashfs, "hashfs", reify=True)
        config.add_request_method(request_renderpath, "renderpath", reify=True)
        config.include(".models")
        config.include("pyramid_mako")
        config.include(admin_views, route_prefix="/admin")
        config.include(static_routes)
    return config.make_wsgi_app()
