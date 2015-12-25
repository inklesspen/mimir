from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.response import FileResponse
import sqlalchemy as sa

from ..models import (
    Writeup,
    WriteupPost,
    )


@view_config(route_name='image')
def image(request):
    address = request.hashfs.get(request.matchdict['path'])
    if address is None:
        raise HTTPNotFound()
    return FileResponse(address.abspath, request=request)


@view_config(route_name='list_writeups', renderer='mimir:templates/list.mako')
def list_writeups(request):
    writeups = request.db_session.query(Writeup)\
        .options(sa.orm.joinedload(Writeup.posts))\
        .filter_by(published=True)\
        .order_by(Writeup.writeup_slug.asc(), Writeup.id.asc())
    return {'writeups': writeups}


@view_config(route_name='writeup', renderer='mimir:templates/writeup.mako')
def writeup(request):
    try:
        writeup = request.db_session.query(Writeup)\
            .options(sa.orm.joinedload(Writeup.posts).joinedload(WriteupPost.active_version))\
            .filter_by(author_slug=request.matchdict['author_slug'],
                       writeup_slug=request.matchdict['writeup_slug'])\
            .one()
    except sa.orm.exc.NoResultFound:
        raise HTTPNotFound()
    return {'writeup': writeup}


@view_config(route_name='admin', renderer='mimir:templates/admin.mako')
def admin(request):
    return {
        'iframeDevtools': request.registry.settings['mimir.react_iframe_devtools'],
        'bootstrap': {
            'root_url': request.route_path('admin', path=''),
            'api_url': request.route_path('api'),
            'squire_url': request.static_path('mimir:static/squire/document.html'),
            'whoami': request.authenticated_userid,
        },
    }


def includeme(config):
    config.add_route('admin', '/admin/*path')
    config.add_route('image', '/images/{path:.*}')
    config.add_route('list_writeups', '/')
    config.add_route('writeup', '/{author_slug}/{writeup_slug}/')
    config.include('pyramid_mako')
    config.scan()
