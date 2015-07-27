from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('.models')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include('.views')
    config.include('.api')
    return config.make_wsgi_app()
