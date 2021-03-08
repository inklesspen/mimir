from markupsafe import Markup
from pyramid.httpexceptions import HTTPForbidden, HTTPSeeOther
from pyramid.view import view_config
import sqlalchemy as sa
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from ..lib.extract import extract_post_into_wpv
from ..lib.fetch import determine_fetches, fetch_thread_page, validate_cred
from ..lib.split import extract_posts, extract_posts_from_pages
from ..models import (
    Credential,
    Thread,
    ThreadPage,
    ThreadPost,
    Writeup,
    WriteupPost,
    WriteupPostVersion,
)
from ..models.classes import likely_writeups
from ..models.mallows import AssignWPV, EditWriteup, EditWriteupPost
from ..render import render_all as perform_render


@view_config(route_name="index", renderer="mimir:templates/index.mako")
def index(request):
    cred = request.db_session.query(Credential).filter_by(valid=True).one_or_none()
    threads = request.db_session.query(Thread).order_by(Thread.id.asc())
    # This is somewhat expensive; there's no index on this.
    # Also this straight up breaks if there's never been any WPVs
    max_tp = request.db_session.query(
        sa.func.max(WriteupPostVersion.threadpost_id)
    ).as_scalar()
    tp = (
        request.db_session.query(ThreadPost)
        .filter(ThreadPost.id == max_tp)
        .options(joinedload(ThreadPost.page))
        .one()
    )

    extracted_wpvs = (
        request.db_session.query(WriteupPostVersion)
        .options(joinedload(WriteupPostVersion.thread_post))
        .filter_by(writeup_post=None)
        .order_by(WriteupPostVersion.id.asc())
        .all()
    )

    for wpv in extracted_wpvs:
        guess = likely_writeups(request.db_session, wpv).first()
        wpv.writeup_guess = guess.title if guess is not None else "[New]"

    writeups = request.db_session.query(Writeup).order_by(
        Writeup.title.collate("writeuptitle").asc(), Writeup.author.asc()
    )

    return {
        "active_cred": cred,
        "threads": threads.all(),
        "last_extracted_post": {
            "thread_id": tp.page.thread.id,
            "page_num": tp.page.page_num,
            "post_id": tp.id,
        },
        "wpvs": extracted_wpvs,
        "writeups": writeups.all(),
    }


@view_config(route_name="thread_page", renderer="mimir:templates/thread_page.mako")
def thread_page(request):
    tp = (
        request.db_session.query(ThreadPage)
        .filter_by(
            thread_id=request.matchdict["thread_id"],
            page_num=request.matchdict["page_num"],
        )
        .options(joinedload(ThreadPage.posts), joinedload(ThreadPage.thread))
        .one()
    )
    for thread_post in tp.posts:
        thread_post.html_markup = Markup(thread_post.html)

    max_page = tp.thread.page_count
    pagination = {
        "enable_prev": tp.page_num > 1,
        "enable_next": tp.page_num < max_page,
        "pages": [],
    }
    page = tp.page_num
    while page > 1 and len(pagination["pages"]) < 2:
        page -= 1
        pagination["pages"].append(page)
    pagination["pages"].reverse()
    page = tp.page_num
    pagination["pages"].append(page)
    while page < max_page and len(pagination["pages"]) < 5:
        page += 1
        pagination["pages"].append(page)

    return {"thread_page": tp, "pagination": pagination}


@view_config(route_name="refetch_page", request_method="POST")
def refetch_page(request):
    thread_page = (
        request.db_session.query(ThreadPage)
        .filter_by(
            thread_id=request.matchdict["thread_id"],
            page_num=request.matchdict["page_num"],
        )
        .options(joinedload(ThreadPage.posts), joinedload(ThreadPage.thread))
        .one()
    )
    fetch_thread_page(
        request.db_session,
        thread_page.fetched_with,
        thread_page.thread_id,
        thread_page.page_num,
    )
    extract_posts(request.db_session, thread_page)
    request.db_session.flush()

    return HTTPSeeOther(location=request.route_path("thread_page", **request.matchdict))


@view_config(route_name="extract_post", request_method="POST")
def extract_post(request):
    thread_post = (
        request.db_session.query(ThreadPost)
        .filter_by(id=request.matchdict["post_id"])
        .one()
    )
    wpv = extract_post_into_wpv(request, thread_post)  # noqa: F841
    request.db_session.flush()

    return HTTPSeeOther(
        location=request.route_path(
            "thread_page",
            thread_id=thread_post.page.thread_id,
            page_num=thread_post.page.page_num,
            _anchor="post-{}".format(thread_post.id),
        )
    )


@view_config(
    route_name="extracted_post",
    renderer="mimir:templates/extracted_post.mako",
    request_method="GET",
)
def extracted_post(request):
    wpv = (
        request.db_session.query(WriteupPostVersion)
        .options(joinedload(WriteupPostVersion.thread_post))
        .filter_by(writeup_post=None)
        .filter_by(id=request.matchdict["post_id"])
        .one()
    )

    ongoing_writeups = request.db_session.query(Writeup).filter_by(status="ongoing")
    likely_writeups_query = likely_writeups(request.db_session, wpv)

    other_writeups = ongoing_writeups.except_(likely_writeups_query).order_by(
        Writeup.title.asc(), Writeup.id.asc()
    )

    wpv.html_markup = Markup(wpv.html_with_fixed_image_urls(request))

    all_likely_writeups = likely_writeups_query.all()
    return {
        "wpv": wpv,
        "other_writeups": other_writeups.all(),
        "likely_writeups": all_likely_writeups,
        "has_likely_writeup": len(all_likely_writeups) > 0,
    }


@view_config(route_name="extracted_post", request_method="POST")
def extracted_post_save(request):
    wpv = (
        request.db_session.query(WriteupPostVersion)
        .options(joinedload(WriteupPostVersion.thread_post))
        .filter_by(writeup_post=None)
        .filter_by(id=request.matchdict["post_id"])
        .one()
    )
    schema = AssignWPV(context={"request": request})
    data = schema.load(request.POST)
    if "writeup_post" in data:
        # existing post, new version
        wp = data["writeup_post"]
        for version in wp.versions:
            version.active = False

        wpv.version = max([x.version for x in wp.versions]) + 1
        wp.versions.append(wpv)

    elif "writeup" in data:
        # existing writeup, new post
        w = data["writeup"]
        new_index = len(w.posts) + 1
        wp = WriteupPost(
            author=wpv.thread_post.author,
            index=new_index,
            ordinal="{}".format(new_index),
            title=data["post_title"],
            published=True,
        )
        w.posts.append(wp)

        wp.versions.append(wpv)
    else:
        # new writeup
        w = Writeup(
            author_slug=Writeup.slugify(data["writeup_author"]),
            writeup_slug=Writeup.slugify(data["writeup_title"]),
            author=data["writeup_author"],
            title=data["writeup_title"],
            status="ongoing",
            published=True,
        )
        request.db_session.add(w)

        wp = WriteupPost(
            author=wpv.thread_post.author,
            index=1,
            ordinal="1",
            title=data["post_title"],
            published=True,
        )
        w.posts.append(wp)

        wp.versions.append(wpv)

    if "post_html" in data:
        new_wpv = WriteupPostVersion()
        new_wpv.html = data["post_html"]
        new_wpv.created_at = sa.func.now()
        new_wpv.version = wpv.version + 1
        new_wpv.active = True

        wpv.writeup_post.versions.append(new_wpv)
        wpv.thread_post.writeup_post_versions.append(new_wpv)
    else:
        wpv.active = True

    request.db_session.flush()
    return HTTPSeeOther(
        location=request.route_path("writeup", writeup_id=wpv.writeup_post.writeup.id)
    )


@view_config(route_name="render_all", request_method="POST")
def render_all(request):
    perform_render(request)
    return HTTPSeeOther(location=request.route_path("rendered_toc"))


@view_config(
    route_name="writeup", renderer="mimir:templates/writeup.mako", request_method="GET"
)
@view_config(
    route_name="writeup_post_options",
    renderer="mimir:templates/extracted_post#writeup_post_options.mako",
)
def writeup_view(request):
    writeup = (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts))
        .filter_by(id=request.matchdict["writeup_id"])
        .one()
    )
    return {"writeup": writeup}


@view_config(route_name="writeup", request_method="POST")
def save_writeup(request):
    writeup = (
        request.db_session.query(Writeup)
        .options(joinedload(Writeup.posts))
        .filter_by(id=request.matchdict["writeup_id"])
        .one()
    )
    schema = EditWriteup(context={"request": request})
    data = schema.load(request.POST)

    writeup.author_slug = data["author_slug"]
    writeup.writeup_slug = data["writeup_slug"]
    writeup.title = data["title"]
    writeup.author = data["author"]
    writeup.status = data["status"]
    writeup.published = data["published"]
    writeup.offensive_content = data["offensive_content"]
    writeup.triggery_content = data["triggery_content"]

    return HTTPSeeOther(location=request.route_path("writeup", writeup_id=writeup.id))


@view_config(
    route_name="writeup_post",
    renderer="mimir:templates/writeup_post.mako",
    request_method="GET",
)
def writeup_post_view(request):
    post = (
        request.db_session.query(WriteupPost)
        .options(joinedload(WriteupPost.writeup))
        .filter_by(
            writeup_id=request.matchdict["writeup_id"],
            index=request.matchdict["post_index"],
        )
        .one()
    )
    return {"post": post, "writeup": post.writeup}


@view_config(
    route_name="writeup_post",
    request_method="POST",
)
def writeup_post_view_save(request):
    post = (
        request.db_session.query(WriteupPost)
        .options(joinedload(WriteupPost.writeup))
        .filter_by(
            writeup_id=request.matchdict["writeup_id"],
            index=request.matchdict["post_index"],
        )
        .one()
    )
    schema = EditWriteupPost(context={"request": request})
    data = schema.load(request.POST)

    post.title = data['title']
    post.author = data['author']
    post.ordinal = data['ordinal']
    post.published = data['published']

    return HTTPSeeOther(
        location=request.route_path(
            "writeup_post", writeup_id=post.writeup_id, post_index=post.index
        )
    )


@view_config(
    route_name="writeup_post_version_preview",
    renderer="mimir:templates/writeup_post_version.mako",
    request_method="GET",
)
@view_config(
    route_name="writeup_post_version_edit",
    renderer="mimir:templates/writeup_post_version.mako",
    request_method="GET",
)
def writeup_post_version(request):
    wpv = (
        request.db_session.query(WriteupPostVersion)
        .join(WriteupPost)
        .filter(
            WriteupPost.writeup_id == request.matchdict["writeup_id"],
            WriteupPost.index == request.matchdict["post_index"],
            WriteupPostVersion.version == request.matchdict["version"],
        )
        .options(
            contains_eager(WriteupPostVersion.writeup_post).joinedload(
                WriteupPost.writeup
            )
        )
        .one()
    )
    route_name = request.matched_route.name
    mode = route_name.split("_")[-1]
    return {
        "wpv": wpv,
        "post": wpv.writeup_post,
        "writeup": wpv.writeup_post.writeup,
        "mode": mode,
    }


@view_config(
    route_name="writeup_post_version_edit",
    request_method="POST",
)
def writeup_post_version_save(request):
    wpv = (
        request.db_session.query(WriteupPostVersion)
        .join(WriteupPost)
        .filter(
            WriteupPost.writeup_id == request.matchdict["writeup_id"],
            WriteupPost.index == request.matchdict["post_index"],
            WriteupPostVersion.version == request.matchdict["version"],
        )
        .options(
            contains_eager(WriteupPostVersion.writeup_post).joinedload(
                WriteupPost.writeup
            )
        )
        .one()
    )
    wp = wpv.writeup_post
    tp = wpv.thread_post
    for _wpv in wp.versions:
        _wpv.active = False
    new_version = max([_wpv.version for _wpv in wp.versions]) + 1
    wpv = WriteupPostVersion()
    wpv.writeup_post = wp
    wpv.thread_post = tp
    wpv.html = request.POST["html"]
    wpv.created_at = sa.func.now()
    wpv.version = new_version
    wpv.active = True
    return HTTPSeeOther(
        location=request.route_path(
            "writeup_post", writeup_id=wp.writeup_id, post_index=wp.index
        )
    )


@view_config(
    route_name="writeup_post_version_activate",
    request_method="POST",
)
def writeup_post_version_activate(request):
    wpv = (
        request.db_session.query(WriteupPostVersion)
        .join(WriteupPost)
        .filter(
            WriteupPost.writeup_id == request.matchdict["writeup_id"],
            WriteupPost.index == request.matchdict["post_index"],
            WriteupPostVersion.version == request.matchdict["version"],
        )
        .options(
            contains_eager(WriteupPostVersion.writeup_post).options(
                joinedload(WriteupPost.writeup), selectinload(WriteupPost.versions)
            )
        )
        .one()
    )
    post = wpv.writeup_post
    for version in post.versions:
        if version is not wpv:
            version.active = False
    wpv.active = True
    return HTTPSeeOther(
        location=request.route_path(
            "writeup_post", writeup_id=post.writeup_id, post_index=post.index
        )
    )


@view_config(route_name="fetch_threads", request_method="POST")
def fetch_threads(request):
    # TODO: handle case where no cred is valid
    cred = request.db_session.query(Credential).filter_by(valid=True).one()
    validate_cred(cred)
    if not cred.valid:
        return HTTPForbidden("Cred invalid")
    fetches = determine_fetches(request.db_session, cred)
    for thread_id, page_num in fetches:
        fetch_thread_page(request.db_session, cred, thread_id, page_num)

    extract_posts_from_pages(request.db_session)
    return HTTPSeeOther(location=request.route_path("index"))


def includeme(config):
    config.add_route("index", "/")
    config.add_route("thread_page", "/threads/{thread_id}/page/{page_num}")
    config.add_route("refetch_page", "/threads/{thread_id}/page/{page_num}/:refetch")
    config.add_route("extract_post", "/post/{post_id}/:extract")
    config.add_route("extracted_post", "/post/{post_id}")
    config.add_route("writeup", "/writeup/{writeup_id}")
    config.add_route("writeup_post_options", "/writeup/{writeup_id}/post-options")
    config.add_route("writeup_post", "/writeup/{writeup_id}/post/{post_index}")
    config.add_route(
        "writeup_post_version_preview",
        "/writeup/{writeup_id}/post/{post_index}/version/{version}",
    )
    config.add_route(
        "writeup_post_version_edit",
        "/writeup/{writeup_id}/post/{post_index}/version/{version}/edit",
    )
    config.add_route(
        "writeup_post_version_activate",
        "/writeup/{writeup_id}/post/{post_index}/version/{version}/activate",
    )
    config.add_route("render_all", "/render")
    config.add_route("fetch_threads", "/fetchthreads")
    config.scan()
