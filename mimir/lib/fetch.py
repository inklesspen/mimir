import sqlalchemy as sa
import requests
from collections import deque
from time import sleep
from ..models import Thread, ThreadPage
from bs4 import BeautifulSoup


def fetch_threads(db_session, cred, limit=None):
    threads = deque([t.id for t in db_session.query(Thread).order_by(Thread.id.asc())])
    pages_fetched = 0
    while len(threads) > 0 and (limit is None or limit > pages_fetched):
        if pages_fetched > 0:
            # sleep for 20 seconds
            sleep(20)
        current_thread = db_session.query(Thread).get(threads.popleft())
        if current_thread.closed and \
           current_thread.page_count == len(current_thread.pages):
            continue
        refetching = False
        # if page_count is 0, always fetch first page
        # else if we have more pages to fetch, fetch the next page
        # else if not closed, re-fetch the last page and compare it
        if current_thread.page_count == 0:
            page_to_fetch = 1
        else:
            last_fetched = max(p.page_num for p in current_thread.pages)
            if current_thread.page_count > last_fetched:
                page_to_fetch = last_fetched + 1
            elif not current_thread.closed:
                page_to_fetch = last_fetched
                refetching = True
            else:
                continue

        print("Fetching page {} of thread {!r}".format(page_to_fetch, current_thread))
        resp = fetch_thread_page(current_thread.id, page_to_fetch, cred.cookies)
        soup = make_soup(resp)
        page_count = extract_page_count(soup)
        current_thread.page_count = page_count
        current_thread.closed = extract_closed(soup)
        if refetching:
            page = [p for p in current_thread.pages if p.page_num == page_to_fetch][0]
        else:
            page = ThreadPage(page_num=page_to_fetch)
            current_thread.pages.append(page)
        page.last_fetched = sa.func.now()
        page.fetched_with = cred
        page.html = str(soup)
        if current_thread.page_count > page.page_num:
            # Not done processing
            threads.appendleft(current_thread.id)
        pages_fetched += 1


def make_soup(resp):
    soup = BeautifulSoup(resp.text, features='lxml')
    return soup


def extract_page_count(soup):
    pages = soup.find(class_="pages")
    return max([int(o['value']) for o in pages.find_all('option')])


def extract_closed(soup):
    buttons = soup.find(class_="postbuttons")
    return 'closed' in buttons.find(alt="Reply")['src']


def fetch_thread_page(thread_id, page_num, cookies=None):
    if cookies is None:
        cookies = {}
    params = {
        'threadid': thread_id,
        'pagenumber': page_num,
        'noseen': 1,
    }
    headers = {
        'User-Agent': "mimir"
    }
    url = 'http://forums.somethingawful.com/showthread.php'
    return requests.get(url, params=params, cookies=cookies, headers=headers)
