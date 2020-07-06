from markupsafe import Markup
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from ..lib.extract import extract_post_into_wpv
from ..lib.fetch import fetch_thread_page
from ..lib.split import extract_posts
from ..models import (
    Thread,
    ThreadPage,
    ThreadPost,
    Writeup,
    WriteupPostVersion,
)
from ..models.classes import likely_writeups


@view_config(route_name="index", renderer="mimir:templates/index.mako")
def index(request):
    threads = request.db_session.query(Thread).order_by(Thread.id.asc())
    # This is somewhat expensive; there's no index on this.
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
        Writeup.title.asc(), Writeup.author.asc()
    )
    # .options(joinedload(Writeup.posts))

    return {
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
    route_name="extracted_post", renderer="mimir:templates/extracted_post.mako"
)
def extracted_post(request):
    wpv = (
        request.db_session.query(WriteupPostVersion)
        .options(joinedload(WriteupPostVersion.thread_post))
        .filter_by(id=request.matchdict["post_id"])
        .one()
    )

    wpv.html_markup = Markup(wpv.html_with_fixed_image_urls(request))

    return {
        "wpv": wpv,
        "likely_writeups": likely_writeups(request.db_session, wpv).all(),
    }


def includeme(config):
    config.add_route("index", "/")
    config.add_route("thread_page", "/threads/{thread_id}/page/{page_num}")
    config.add_route("refetch_page", "/threads/{thread_id}/page/{page_num}/:refetch")
    config.add_route("extract_post", "/post/{post_id}/:extract")
    config.add_route("extracted_post", "/post/{post_id}")
    config.add_route("writeup", "/writeup/{writeup_id}")
    config.scan()
