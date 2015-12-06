import sqlalchemy as sa
from sqlalchemy import or_, null
from collections import namedtuple
import bs4
from dateutil.parser import parse
import pytz

from ..models import ThreadPage, ThreadPost

Post = namedtuple("Post", ("id", "author", "timestamp", "html"))


def is_comment(text):
    return isinstance(text, bs4.element.Comment)


def split_threadpage(page, tz):
    posts = []
    soup = bs4.BeautifulSoup(page.html, 'lxml')
    post_tags = soup.findAll("table", class_="post")
    for post_tag in post_tags:
        id = int(post_tag['id'][4:])
        # there are some other strings from <a> tags in here
        timestring = tuple(post_tag.find(class_="postdate").stripped_strings)[-1]
        timestamp = tz.localize(parse(timestring))
        author = post_tag.find(class_="author").string
        div = soup.new_tag("div")
        postbody = post_tag.find(class_="postbody")
        wrapped = postbody.wrap(div)
        postbody.unwrap()
        # now the <td> has been replaced by a <div>
        # remove comments
        for comment in wrapped.findAll(text=is_comment):
            comment.extract()
        # remove editedby if necessary
        editedby = wrapped.find("p", class_="editedby")
        if editedby is not None:
            editedby.extract()
        html = wrapped.prettify(formatter="html").strip()
        posts.append(Post(id=id, author=author, timestamp=timestamp, html=html))
    return posts


def extract_posts(db_session, page, tz):
    posts = split_threadpage(page, tz)
    if page.last_split is None:
        # splitting for the first time, no need to check if posts exist
        for post_data in posts:
            post = ThreadPost(thread=page.thread,
                              page=page,
                              last_extracted=sa.func.now(),
                              **vars(post_data))
            page.posts.append(post)
    elif page.last_fetched > page.last_split:
        # potentially some new posts or updated posts
        for post_data in posts:
            with db_session.no_autoflush:
                post = db_session.query(ThreadPost).get(post_data.id)
            if post is None:
                post = ThreadPost(thread=page.thread,
                                  page=page,
                                  last_extracted=sa.func.now(),
                                  **vars(post_data))
                page.posts.append(post)
            else:
                post.last_extracted = sa.func.now()
                # the html is the only thing that can change
                post.html = post_data.html
    page.last_split = sa.func.now()
    db_session.flush()


def extract_posts_from_pages(db_session):
    for page in db_session.query(ThreadPage).filter(
            or_(ThreadPage.last_split == null(),
                ThreadPage.last_fetched > ThreadPage.last_split)):
        tz = pytz.timezone(page.fetched_with.timezone)
        extract_posts(db_session, page, tz)
