from bs4 import BeautifulSoup
from ftfy import bad_codecs
import requests
import sqlalchemy as sa
from urllib.parse import urlparse, parse_qs

from ..models import Thread, ThreadPage, ThreadPost

bad_codecs.ok()  # load in the sloppy codecs


def validate_cred(cred):
    resp = fetch_sa_page(
        "https://forums.somethingawful.com/usercp.php", {}, cred.cookies
    )
    soup = make_soup(resp)
    cred.valid = soup.find(id="unregistered") is None
    cred.username = soup.find(id="loggedinusername").text


def get_cred_timezone_offset(cred):
    # https://forums.somethingawful.com/member.php?action=editoptions
    resp = fetch_sa_page(
        "https://forums.somethingawful.com/member.php",
        {"action": "editoptions"},
        cred.cookies,
    )
    soup = make_soup(resp)
    tzo = soup.find(attrs={"name": "timezoneoffset"})
    hour_offset_str = tzo.find(selected=True)["value"]
    hour_offset = float(hour_offset_str)
    is_dst = soup.find(attrs={"name": "use_dst", "checked": True})["value"] == "yes"
    if is_dst:
        hour_offset += 1
    second_offset = hour_offset * 60 * 60
    return second_offset


def update_thread_status(thread, cred):
    resp = _fetch_thread_page_html(thread.id, 1, cred)
    soup = make_soup(resp)
    page_count = extract_page_count(soup)
    thread.page_count = page_count
    thread.closed = extract_closed(soup)


def determine_fetches(db_session, cred):
    for thread in db_session.query(Thread).filter_by(closed=False):
        update_thread_status(thread, cred)
    db_session.flush()
    incomplete_page_ids = (
        sa.select(ThreadPost.page_id)
        .group_by(ThreadPost.page_id)
        .having(sa.func.count(ThreadPost.id) < 40)
        .scalar_subquery()
    )
    incomplete_pages = (
        sa.select(
            ThreadPage.thread_id,
            ThreadPage.page_num,
        )
        .select_from(sa.join(ThreadPage, Thread))
        .where(
            sa.and_(ThreadPage.id.in_(incomplete_page_ids), Thread.closed == sa.false())
        )
    )
    fetch_status = (
        sa.select(
            ThreadPage.thread_id.label("thread_id"),
            sa.func.max(ThreadPage.page_num).label("last_fetched_page"),
        )
        .group_by(ThreadPage.thread_id)
        .subquery("fetch_status")
    )
    unfetched_pages = sa.select(
        Thread.id.label("thread_id"),
        sa.func.generate_series(
            fetch_status.c.last_fetched_page + 1, Thread.page_count
        ).label("page_num"),
    ).select_from(sa.join(Thread, fetch_status, Thread.id == fetch_status.c.thread_id))
    fetched_first_pages = (
        sa.select(ThreadPage.thread_id)
        .where(ThreadPage.page_num == 1)
        .scalar_subquery()
    )
    unfetched_first_pages = (
        sa.select(
            Thread.id.label("thread_id"),
            sa.literal(1, sa.Integer).label("page_num"),
        )
        .select_from(Thread)
        .where(Thread.id.notin_(fetched_first_pages))
    )
    q = sa.union(incomplete_pages, unfetched_pages, unfetched_first_pages)
    q = q.order_by(
        q.selected_columns.thread_id.asc(), q.selected_columns.page_num.asc()
    )
    return db_session.execute(q).fetchall()


def fetch_thread_page(db_session, cred, thread_id, page_num, offset):
    resp = _fetch_thread_page_html(thread_id, page_num, cred)
    soup = make_soup(resp)

    # Inline the ignored posts
    for ignored_link in soup.find_all(class_="ignored-post-link"):
        ignored_params = parse_qs(urlparse(ignored_link["href"]).query)
        post_el = ignored_link.find_parent("table", class_="post")
        ignored_post_page_resp = fetch_sa_page_with_cred(ignored_params, cred)
        ignored_soup = make_soup(ignored_post_page_resp)
        ignored_post_el = ignored_soup.find(id=post_el["id"])
        post_el.replace_with(ignored_post_el)

    thread = db_session.query(Thread).filter_by(id=thread_id).one()
    if page_num in thread.pages_by_pagenum:
        page = thread.pages_by_pagenum[page_num]
    else:
        page = ThreadPage(page_num=page_num)
        thread.pages.append(page)

    page.last_fetched = sa.func.now()
    page.fetched_with = cred
    page.html = str(soup)
    page.utc_offset_at_fetch = offset

    db_session.flush()


def make_soup(resp):
    return make_soup_from_html(resp.text)


def make_soup_from_html(html):
    soup = BeautifulSoup(html, features="lxml")
    return soup


def extract_page_count(soup):
    pages = soup.find(class_="pages")
    page_options = pages.find_all("option")
    if page_options:
        return max([int(o["value"]) for o in page_options])
    else:
        return 1


def extract_closed(soup):
    buttons = soup.find(class_="postbuttons")
    return buttons.find(alt="Reply") is None


def _fetch_thread_page_html(thread_id, page_num, cred):
    params = {
        "threadid": thread_id,
        "pagenumber": page_num,
        "noseen": 1,
        "perpage": 40,
    }
    return fetch_sa_page_with_cred(params, cred)


def fetch_sa_page_with_cred(params, cred):
    url = "http://forums.somethingawful.com/showthread.php"
    return fetch_sa_page(url, params, cred.cookies)


def fetch_sa_page(url, params, cookies=None):
    if cookies is None:
        cookies = {}
    headers = {"User-Agent": "mimir"}
    resp = requests.get(url, params=params, cookies=cookies, headers=headers)
    # if we have 'iso-8859-1', it should actually be 'windows-1252'
    if resp.encoding == "iso-8859-1":
        resp.encoding = "sloppy-windows-1252"
    return resp
