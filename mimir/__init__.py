import hashfs
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy


def request_hashfs(request):
    path = request.registry.settings['hashfs']['location']
    fs = hashfs.HashFS(path, depth=2, width=3, algorithm='sha256')
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
    AuthorizedUser = config.maybe_dotted('.models.AuthorizedUser')
    authn_policy = AuthTktAuthenticationPolicy(
        secret='I am a big dumb stupid', hashalg='sha512', callback=AuthorizedUser.check)
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    return config.make_wsgi_app()
