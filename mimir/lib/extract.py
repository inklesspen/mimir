import bs4
from ..models import WriteupPostVersion as WPV
from .images import mirror_image, MirrorError
from urllib.parse import urljoin
import time


def extract_post(request, wpv_id, self_html=False, sleep_between=False):
    """
    1) soupify
    2) mirror all images
    2a) put size info into img tag, along with original url
    2b) remove timg class
    3) adjust all relative urls ??? example at threadpost 427984253
    4) add rel=nofollow to links
    """

    wpv = request.db_session.query(WPV).filter_by(id=wpv_id).one()
    return extract_post_from_wpv(request, wpv, self_html, sleep_between)


def extract_post_from_wpv(request, wpv, self_html=False, sleep_between=False):
    if self_html:
        html = wpv.html
    else:
        html = wpv.thread_post.html
    soup = bs4.BeautifulSoup(html, 'lxml')
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

    div = soup.div.extract()
    div.hidden = True
    wpv.html = div.prettify(formatter="html")
