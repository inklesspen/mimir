import sqlalchemy as sa
import requests
from ..models import Thread, ThreadPage, ThreadPost
from bs4 import BeautifulSoup


def update_thread_status(thread, cred):
    resp = fetch_thread_page_html(thread.id, 1, cred.cookies)
    soup = make_soup(resp)
    page_count = extract_page_count(soup)
    thread.page_count = page_count
    thread.closed = extract_closed(soup)


def determine_fetches(db_session, cred):
    for thread in db_session.query(Thread).filter_by(closed=False):
        update_thread_status(thread, cred)
    db_session.flush()
    incomplete_page_ids = sa.select([ThreadPost.page_id])\
        .group_by(ThreadPost.page_id).having(sa.func.count(ThreadPost.id) < 40)\
        .as_scalar()
    incomplete_pages = sa.select([ThreadPage.thread_id, ThreadPage.page_num], from_obj=sa.join(ThreadPage, Thread))\
        .where(sa.and_(ThreadPage.id.in_(incomplete_page_ids), Thread.closed == sa.false()))
    fetch_status = sa.select(
        [
            ThreadPage.thread_id.label('thread_id'),
            sa.func.max(ThreadPage.page_num).label('last_fetched_page'),
        ]).group_by(ThreadPage.thread_id).alias('fetch_status')
    unfetched_pages = sa.select(
        [
            Thread.id.label('thread_id'),
            sa.func.generate_series(fetch_status.c.last_fetched_page+1, Thread.page_count).label('page_num'),
        ], from_obj=sa.join(Thread, fetch_status, Thread.id == fetch_status.c.thread_id))
    q = incomplete_pages.union(unfetched_pages)
    q = q.order_by(q.c.thread_id.asc(), q.c.page_num.asc())
    return db_session.execute(q).fetchall()


def fetch_thread_page(db_session, cred, thread_id, page_num):
    resp = fetch_thread_page_html(thread_id, page_num, cred.cookies)
    soup = make_soup(resp)

    thread = db_session.query(Thread).filter_by(id=thread_id).one()
    if page_num in thread.pages_by_pagenum:
        page = thread.pages_by_pagenum[page_num]
    else:
        page = ThreadPage(page_num=page_num)
        thread.pages.append(page)

    page.last_fetched = sa.func.now()
    page.fetched_with = cred
    page.html = str(soup)

    db_session.flush()


def make_soup(resp):
    soup = BeautifulSoup(resp.text, features='lxml')
    return soup


def extract_page_count(soup):
    pages = soup.find(class_="pages")
    return max([int(o['value']) for o in pages.find_all('option')])


def extract_closed(soup):
    buttons = soup.find(class_="postbuttons")
    return 'closed' in buttons.find(alt="Reply")['src']


def fetch_thread_page_html(thread_id, page_num, cookies=None):
    if cookies is None:
        cookies = {}
    params = {
        'threadid': thread_id,
        'pagenumber': page_num,
        'noseen': 1,
        'perpage': 40,
    }
    headers = {
        'User-Agent': "mimir"
    }
    url = 'http://forums.somethingawful.com/showthread.php'
    return requests.get(url, params=params, cookies=cookies, headers=headers)
