import hashfs
from pyramid.config import Configurator


def request_hashfs(request):
    path = request.registry.settings['hashfs']['location']
    fs = hashfs.HashFS(path, depth=3, width=2, algorithm='sha256')
    return fs


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('.models')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include('.views')
    config.include('.api')

    config.add_request_method(request_hashfs, 'hashfs', reify=True)

    return config.make_wsgi_app()
