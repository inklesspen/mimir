import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from pyramid_rpc.jsonrpc import jsonrpc_method

from ..models import (
    mallows,
    Thread,
    ThreadPage,
    ThreadPost,
    Writeup,
    WriteupPost,
    WriteupPostVersion,
    )

from ..lib.extract import extract_post_from_wpv


@jsonrpc_method(endpoint='api')
def thread_info(request):
    query = request.db_session.query(Thread).order_by(Thread.id.asc())
    return [{
        'id': t.id,
        'page_count': t.page_count,
        'closed': t.closed,
    } for t in query]


@jsonrpc_method(endpoint='api')
def thread_page(request, thread_id, page_num):
    tp = request.db_session.query(ThreadPage)\
        .filter_by(thread_id=thread_id, page_num=page_num)\
        .options(joinedload(ThreadPage.posts), joinedload(ThreadPage.thread))\
        .one()
    schema = mallows.ThreadPost(many=True)
    return {
        'thread_id': tp.thread_id,
        'page_num': tp.page_num,
        'page_count': tp.thread.page_count,
        'posts': schema.dump(tp.posts).data,
    }


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
    schema = mallows.Writeup()
    return schema.dump(query.one()).data


@jsonrpc_method(endpoint='api')
def save_writeup(request, writeup):
    if 'id' in writeup:
        obj = request.db_session.query(Writeup)\
            .filter(Writeup.id == writeup['id'])\
            .one()
        for unsettable in ['id', 'posts', 'author_slug', 'writeup_slug']:
            if unsettable in writeup:
                del writeup[unsettable]
    else:
        # possibly this isn't quite right yet; we'll see
        obj = Writeup()
        request.db_session.add(obj)
    for key, value in writeup.items():
        setattr(obj, key, value)
    request.db_session.flush()
    schema = mallows.Writeup()
    return schema.dump(obj).data


@jsonrpc_method(endpoint='api')
def post_detail(request, writeup_id, post_index):
    query = request.db_session.query(WriteupPost)\
        .filter(WriteupPost.writeup_id == writeup_id)\
        .filter(WriteupPost.index == post_index)\
        .options(joinedload(WriteupPost.versions))
    schema = mallows.WriteupPost()
    return schema.dump(query.one()).data


@jsonrpc_method(endpoint='api')
def extract_post(request, thread_post_id):
    tp = request.db_session.query(ThreadPost).filter_by(id=thread_post_id).one()
    wpv = WriteupPostVersion(thread_post=tp, created_at=sa.func.now())
    request.db_session.add(wpv)
    with request.db_session.no_autoflush:
        extract_post_from_wpv(request, wpv)
    wpv.edit_summary = "Extracted from post {}".format(tp.id)
    request.db_session.flush()
    schema = mallows.WriteupPostVersion()
    return schema.dump(wpv).data


@jsonrpc_method(endpoint='api')
def say_hello(request, name):
    return "Hello, {}!".format(name)


def includeme(config):
    config.include('pyramid_rpc.jsonrpc')
    config.add_jsonrpc_endpoint('api', '/api', default_renderer='json')
    config.scan()
