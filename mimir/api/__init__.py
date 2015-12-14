import requests
from pyramid.security import (
    remember, forget,
    Allow, Authenticated, DENY_ALL,
)
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from pyramid_rpc.jsonrpc import jsonrpc_method

from ..models import (
    mallows,
    AuthorizedUser,
    Thread,
    ThreadPage,
    ThreadPost,
    Writeup,
    WriteupPost,
    WriteupPostVersion,
    )

from ..lib.extract import extract_post_from_wpv


@jsonrpc_method(endpoint='api')
def whoami(request):
    return request.authenticated_userid


@jsonrpc_method(endpoint='api')
def login(request, assertion):
    data = {'assertion': assertion, 'audience': 'http://dockerhost:8080/'}
    resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)
    if resp.ok:
        verification_data = resp.json()
        if verification_data['status'] == 'okay':
            email = verification_data['email']
            au = request.db_session.query(AuthorizedUser).filter_by(email=email).one_or_none()
            if au is not None:
                headers = remember(request, email)
                response = request.response
                response.headerlist.extend(headers)
                return {'result': 'ok', 'email': email}
    raise ValueError('Nope')


@jsonrpc_method(endpoint='api')
def logout(request):
    headers = forget(request)
    response = request.response
    response.headerlist.extend(headers)
    return {}


@jsonrpc_method(endpoint='api', permission='admin')
def thread_info(request):
    query = request.db_session.query(Thread).order_by(Thread.id.asc())
    return [{
        'id': t.id,
        'page_count': t.page_count,
        'closed': t.closed,
    } for t in query]


@jsonrpc_method(endpoint='api', permission='admin')
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


@jsonrpc_method(endpoint='api', permission='admin')
def extracted_list(request):
    query = request.db_session.query(WriteupPostVersion)\
        .filter_by(writeup_post=None)\
        .order_by(WriteupPostVersion.id.asc())
    schema = mallows.WriteupPostVersion(many=True)
    return schema.dump(query.all()).data


@jsonrpc_method(endpoint='api', permission='admin')
def writeup_list(request):
    query = request.db_session.query(Writeup)\
        .order_by(Writeup.writeup_slug.asc(), Writeup.author_slug.asc())\
        .options(joinedload(Writeup.posts))
    schema = mallows.Writeup(many=True)
    return schema.dump(query.all()).data


@jsonrpc_method(endpoint='api', permission='admin')
def writeup_detail(request, id):
    query = request.db_session.query(Writeup)\
        .filter(Writeup.id == id)\
        .options(joinedload(Writeup.posts))
    schema = mallows.Writeup()
    return schema.dump(query.one()).data


@jsonrpc_method(endpoint='api', permission='admin')
def save_writeup(request, writeup):
    if 'id' in writeup:
        obj = request.db_session.query(Writeup)\
            .filter(Writeup.id == writeup['id'])\
            .one()
        for unsettable in ['id', 'posts', 'author_slug', 'writeup_slug']:
            if unsettable in writeup:
                del writeup[unsettable]
    else:
        raise NotImplementedError("deprecated!")
        # possibly this isn't quite right yet; we'll see
        obj = Writeup()
        request.db_session.add(obj)
    for key, value in writeup.items():
        setattr(obj, key, value)
    request.db_session.flush()
    schema = mallows.Writeup()
    return schema.dump(obj).data


@jsonrpc_method(endpoint='api', permission='admin')
def post_detail(request, writeup_id, post_index):
    query = request.db_session.query(WriteupPost)\
        .filter(WriteupPost.writeup_id == writeup_id)\
        .filter(WriteupPost.index == post_index)\
        .options(joinedload(WriteupPost.versions))
    schema = mallows.WriteupPost()
    return schema.dump(query.one()).data


@jsonrpc_method(endpoint='api', permission='admin')
def save_post(request, post):
    obj = request.db_session.query(WriteupPost).filter(WriteupPost.id == post['id']).one()

    # TODO: switch to marshmallow
    for unsettable in ['id', 'versions', 'active_version', 'writeup']:
        if unsettable in post:
            del post[unsettable]
    for key, value in post.items():
        setattr(obj, key, value)

    request.db_session.flush()
    schema = mallows.WriteupPost()
    return schema.dump(obj).data


@jsonrpc_method(endpoint='api', permission='admin')
def activate_version(request, wpv_id):
    wpv = request.db_session.query(WriteupPostVersion).filter_by(id=wpv_id).one()
    post = wpv.writeup_post
    for version in post.versions:
        if version is not wpv:
            version.active = False
    wpv.active = True

    request.db_session.flush()
    schema = mallows.WriteupPostVersion()
    return schema.dump(wpv).data


@jsonrpc_method(endpoint='api', permission='admin')
def get_wpv(request, wpv_id):
    query = request.db_session.query(WriteupPostVersion)\
        .filter_by(id=wpv_id)
    schema = mallows.WriteupPostVersion()
    return schema.dump(query.one()).data


@jsonrpc_method(endpoint='api', permission='admin')
def save_wpv(request, wpv_data):
    wp = request.db_session.query(WriteupPost).filter_by(id=wpv_data['writeuppost_id']).one()
    tp = request.db_session.query(ThreadPost).filter_by(id=wpv_data['threadpost_id']).one()
    for _wpv in wp.versions:
        _wpv.active = False
    new_version = max([_wpv.version for _wpv in wp.versions]) + 1
    wpv = WriteupPostVersion()
    wpv.writeup_post = wp
    wpv.thread_post = tp
    wpv.html = wpv_data['html']
    wpv.created_at = sa.func.now()
    wpv.version = new_version
    wpv.active = True
    wpv.edit_summary = wpv_data['edit_summary']

    request.db_session.flush()
    schema = mallows.WriteupPostVersion()
    return schema.dump(wpv).data


@jsonrpc_method(endpoint='api', permission='admin')
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


@jsonrpc_method(endpoint='api', permission='admin')
def delete_extracted(request, wpv_id):
    wpv = request.db_session.query(WriteupPostVersion).filter_by(id=wpv_id, writeup_post=None).one()
    request.db_session.delete(wpv)


@jsonrpc_method(endpoint='api', permission='admin')
def attach_extracted(request, wpv_id, target):
    wpv = request.db_session.query(WriteupPostVersion).filter_by(id=wpv_id, writeup_post=None).one()

    schema = mallows.InputVersionExistingPost()
    result = schema.load(target)
    if not result.errors:
        w = request.db_session.query(Writeup).filter_by(id=result.data['w_id']).one()
        wp = request.db_session.query(WriteupPost).filter_by(writeup=w, index=result.data['wp_index']).one()
        wpv.version = max([x.version for x in wp.versions]) + 1

        wp.versions.append(wpv)
        request.db_session.flush()
        schema = mallows.WriteupPostVersion()
        return schema.dump(wpv).data

    schema = mallows.InputVersionNewPost()
    result = schema.load(target)
    if not result.errors:
        w = request.db_session.query(Writeup).filter_by(id=result.data['w_id']).one()
        new_index = len(w.posts) + 1
        wp = WriteupPost(
            author=wpv.thread_post.author,
            index=new_index,
            ordinal='{}'.format(new_index),
            title=result.data['wp_title'],
            published=False
        )
        w.posts.append(wp)

        wp.versions.append(wpv)
        wpv.active = True
        request.db_session.flush()
        schema = mallows.WriteupPostVersion()
        return schema.dump(wpv).data

    schema = mallows.InputVersionNewWriteup()
    result = schema.load(target)
    if not result.errors:
        w = Writeup(
            author_slug=Writeup.slugify(result.data['w_author']),
            writeup_slug=Writeup.slugify(result.data['w_title']),
            title=result.data['w_title'],
            status='ongoing',
            published=False,
        )
        request.db_session.add(w)

        wp = WriteupPost(
            author=wpv.thread_post.author,
            index=1,
            ordinal='1',
            title=result.data['wp_title'],
            published=False
        )
        w.posts.append(wp)

        wp.versions.append(wpv)
        wpv.active = True
        request.db_session.flush()
        schema = mallows.WriteupPostVersion()
        return schema.dump(wpv).data
    raise ValueError(result.errors)


@jsonrpc_method(endpoint='api')
def say_hello(request, name):
    return "Hello, {}!".format(name)


class AdminContext(object):
    __acl__ = [
        (Allow, Authenticated, 'admin'),
        DENY_ALL
    ]

    def __init__(self, request):
        pass


def includeme(config):
    config.include('pyramid_rpc.jsonrpc')
    config.add_jsonrpc_endpoint('api', '/api', default_renderer='json', factory=AdminContext)
    config.scan()
