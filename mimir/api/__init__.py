from sqlalchemy.orm import joinedload
from pyramid_rpc.jsonrpc import jsonrpc_method

from ..models import (
    Thread,
    Writeup,
    )


@jsonrpc_method(endpoint='api')
def thread_info(request):
    query = request.db_session.query(Thread).order_by(Thread.id.asc())
    return [{
        'id': t.id,
        'page_count': t.page_count,
        'closed': t.closed,
    } for t in query]


@jsonrpc_method(endpoint='api')
def writeup_list(request):
    query = request.db_session.query(Writeup)\
        .order_by(Writeup.writeup_slug.asc(), Writeup.author_slug.asc())\
        .options(joinedload(Writeup.posts))
    return [{
        'id': w.id,
        'author_slug': w.author_slug,
        'writeup_slug': w.writeup_slug,
        'title': w.title,
        'status': w.status,
        'published': w.published,
        'offensive_content': w.offensive_content,
        'triggery_content': w.triggery_content,
        'post_count': len(w.posts),
    } for w in query]


@jsonrpc_method(endpoint='api')
def writeup_detail(request, id):
    query = request.db_session.query(Writeup)\
        .filter(Writeup.id == id)\
        .options(joinedload(Writeup.posts))
    return query.one()


@jsonrpc_method(endpoint='api')
def say_hello(request, name):
    return "Hello, {}!".format(name)


def includeme(config):
    config.include('pyramid_rpc.jsonrpc')
    config.add_jsonrpc_endpoint('api', '/api', default_renderer='json')
    config.scan()
