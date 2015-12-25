import bs4
from .images import mirror_image, MirrorError
from urllib.parse import urljoin
import time


def extract_post_from_wpv(request, wpv, self_html=False, sleep_between=False):
    """
    1) soupify
    2) mirror all images
    2a) put size info into img tag, along with original url
    2b) remove timg class
    3) adjust all relative urls ??? example at threadpost 427984253
    4) add rel=nofollow to links
    """

    if self_html:
        html = wpv.html
    else:
        html = wpv.thread_post.html
    soup = open_soup(html)
    # referer should not contain the fragment identifier, so just the page url
    referer = wpv.thread_post.page.url

    for img_tag in soup.find_all('img'):
        try:
            did_fetch = mirror_image(request, img_tag, referer)
            if did_fetch and sleep_between:
                time.sleep(1)
        except MirrorError:
            pass

        if 'class' in img_tag and 'timg' in img_tag['class']:
            img_tag['class'].remove('timg')

    for a_tag in soup.find_all('a', href=True):
        a_tag['href'] = urljoin(wpv.thread_post.url, a_tag['href'])
        a_tag['rel'] = 'nofollow'

    wpv.html = close_soup(soup)


def open_soup(html):
    soup = bs4.BeautifulSoup(html, 'lxml')
    return soup


def _find_container(soup):
    body_tags = soup.body.find_all(lambda el: isinstance(el, bs4.element.Tag), recursive=False)
    if len(body_tags) == 1 and body_tags[0].name == 'div':
        return soup.body.div
    return soup.body


def close_soup(soup):
    container = _find_container(soup)
    container = container.extract()
    container.hidden = True
    html = container.prettify(formatter="html")
    return html
