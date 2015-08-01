from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
import sqlalchemy as sa

from ..models import (
    Writeup,
    )


@view_config(route_name='list_writeups', renderer='mimir:templates/list.mako')
def list_writeups(request):
    writeups = request.db_session.query(Writeup)\
        .options(sa.orm.joinedload(Writeup.posts))\
        .filter_by(published=True)\
        .order_by(Writeup.writeup_slug.asc(), Writeup.author_slug.asc())
    return {'writeups': writeups}


@view_config(route_name='writeup', renderer='mimir:templates/writeup.mako')
def writeup(request):
    try:
        writeup = request.db_session.query(Writeup)\
            .options(sa.orm.joinedload(Writeup.posts))\
            .filter_by(author_slug=request.matchdict['author_slug'],
                       writeup_slug=request.matchdict['writeup_slug'])\
            .one()
    except sa.orm.exc.NoResultFound:
        raise HTTPNotFound()
    return {'writeup': writeup}


@view_config(route_name='admin', renderer='mimir:templates/admin.mako')
def admin(request):
    return {
        'iframeDevtools': request.registry.settings['mimir.react_iframe_devtools']
    }


def includeme(config):
    config.add_route('list_writeups', '/')
    config.add_route('writeup', '/{author_slug}/{writeup_slug}/')
    config.add_route('admin', '/admin/*path')
    config.include('pyramid_mako')
    config.scan()
