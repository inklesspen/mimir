from pyramid_rpc.jsonrpc import jsonrpc_method

from ..models import (
    Thread,
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
def say_hello(request, name):
    return "Hello, {}!".format(name)


def includeme(config):
    config.include('pyramid_rpc.jsonrpc')
    config.add_jsonrpc_endpoint('api', '/api')
    config.scan()
