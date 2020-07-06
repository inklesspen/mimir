import re

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Unicode,
    UnicodeText,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from .column_types import AwareDateTime
from .meta import Base


class AuthorizedUser(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    name = Column(Unicode, nullable=False)

    @classmethod
    def check(cls, candidate_username, request):
        users = request.registry.settings["users"]
        if candidate_username in users:
            return []
        return None


class Credential(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    cookies = Column(JSONB, nullable=False)
    timezone = Column(String(32), nullable=False)
    valid = Column(Boolean, nullable=False, default=sa.true())


class AuditEntry(Base):
    __tablename__ = "audit_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("authorized_users.id"), nullable=False)
    text = Column(Unicode, nullable=False)
    timestamp = Column(AwareDateTime, nullable=False)

    user = relationship("AuthorizedUser", uselist=False)


class Thread(Base):
    # TODO: prevent a sequence from being made for this
    id = Column(Integer, primary_key=True)
    closed = Column(Boolean, nullable=False, default=False)
    # This should be actual page count, not merely the last fetched
    # 0 means we have not yet fetched anything
    page_count = Column(Integer, nullable=False)
    pages = relationship("ThreadPage", backref="thread")
    posts = relationship("ThreadPost", backref="thread")

    pages_by_pagenum = relationship(
        "ThreadPage", collection_class=attribute_mapped_collection("page_num"),
    )

    @property
    def url(self):
        return "https://forums.somethingawful.com/showthread.php?threadid={}".format(
            self.id
        )


class ThreadPage(Base):
    __table_args__ = (UniqueConstraint("thread_id", "page_num"),)
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    page_num = Column(Integer, nullable=False)
    html = Column(UnicodeText, nullable=False)
    last_fetched = Column(AwareDateTime, nullable=False)
    last_split = Column(AwareDateTime, nullable=True)
    fetched_with_id = Column(Integer, ForeignKey("credentials.id"), nullable=False)
    # TODO: add timezone here
    # TODO: allow multiple fetches, generally only caring about the latest one
    # but keeping the rest around just in case?
    posts = relationship("ThreadPost", backref="page", order_by="ThreadPost.id")
    fetched_with = relationship("Credential", uselist=False)

    @property
    def url(self):
        return "{}&pagenumber={}".format(self.thread.url, self.page_num)


class ThreadPost(Base):
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("thread_pages.id"), nullable=False)
    author = Column(Unicode(40), nullable=False)
    timestamp = Column(AwareDateTime, nullable=False)
    html = Column(UnicodeText, nullable=False)
    last_extracted = Column(AwareDateTime, nullable=False)

    writeup_post_versions = relationship("WriteupPostVersion", backref="thread_post")

    def __repr__(self):
        return "<ThreadPost {self.id}: thread {self.thread_id} page {self.page.page_num}>".format(
            self=self
        )

    @property
    def url(self):
        return "{}#post{}".format(self.page.url, self.id)

    @property
    def has_been_extracted(self):
        return len(self.writeup_post_versions) > 0

    @property
    def is_in_writeup(self):
        w = [wpv for wpv in self.writeup_post_versions if wpv.writeup_post is not None]
        return len(w) > 0


class Writeup(Base):
    __table_args__ = (UniqueConstraint("author_slug", "writeup_slug"),)
    id = Column(Integer, primary_key=True)
    author_slug = Column(String(100), nullable=False, index=True)
    writeup_slug = Column(String(100), nullable=False, index=True)
    title = Column(Unicode(100), nullable=False)
    author = Column(Unicode(100), nullable=False)
    status = Column(
        Enum("ongoing", "abandoned", "completed", native_enum=False), nullable=False
    )
    published = Column(Boolean, nullable=False, default=False)
    # anything with offensive_content will be blocked in robots.txt
    # this is for reviews of stuff that is unredeemable shit
    offensive_content = Column(Boolean, nullable=False, default=False)
    # this is for reviews of stuff that respectfully handle triggery shit
    triggery_content = Column(Boolean, nullable=False, default=False)

    posts = relationship(
        "WriteupPost",
        backref="writeup",
        order_by="WriteupPost.index",
        cascade="all, delete-orphan",
    )

    published_posts = relationship(
        "WriteupPost",
        viewonly=True,
        order_by="WriteupPost.index",
        primaryjoin=(
            "and_(Writeup.id == WriteupPost.writeup_id, "
            "WriteupPost.published == true())"
        ),
    )

    def __repr__(self):
        return '<Writeup {self.id}: "{self.title}>"'.format(self=self)

    @staticmethod
    def slugify(value):
        slug = value.lower()
        slug = re.sub("[^ .&0-9a-z]", "", slug)
        slug = slug.replace(" & ", "and")
        slug = slug.replace("&", "-and-")
        slug = slug.replace(" ", "-")
        slug = slug.replace(".", "-")
        return slug.strip("-")


class WriteupPost(Base):
    id = Column(Integer, primary_key=True)
    writeup_id = Column(Integer, ForeignKey("writeups.id"), nullable=False)
    author = Column(Unicode(40), nullable=False)
    index = Column(Integer, nullable=False)
    # Some posts have 1.5 and so on, but I don't want to use floats
    ordinal = Column(Unicode(5), nullable=False)
    title = Column(Unicode, nullable=True)
    published = Column(Boolean, nullable=False, default=False)

    versions = relationship(
        "WriteupPostVersion",
        backref="writeup_post",
        cascade="all, delete-orphan",
        order_by="WriteupPostVersion.version.desc()",
    )

    active_version = relationship(
        "WriteupPostVersion",
        viewonly=True,
        uselist=False,
        primaryjoin=(
            "and_(WriteupPost.id == WriteupPostVersion.writeuppost_id, "
            "WriteupPostVersion.active == true())"
        ),
    )

    def __repr__(self):
        return '<WriteupPost {self.id} of {self.writeup!r}: {self.index}, "{self.title}">'.format(
            self=self
        )


class WriteupPostVersion(Base):
    __table_args__ = (
        CheckConstraint(
            sa.or_(
                sa.column("writeuppost_id") != sa.null(),
                sa.column("active") == sa.false(),
            ),
            name="check_attachment",
        ),
    )
    id = Column(Integer, primary_key=True)
    writeuppost_id = Column(Integer, ForeignKey("writeup_posts.id"), nullable=True)
    html = Column(UnicodeText, nullable=True)
    threadpost_id = Column(Integer, ForeignKey("thread_posts.id"), nullable=False)
    created_at = Column(AwareDateTime, nullable=False)

    version = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, nullable=False, default=False)

    edit_summary = Column(Unicode(200), nullable=False)

    url = association_proxy("thread_post", "url")

    def html_with_fixed_image_urls(self, request):
        from ..lib.extract import open_soup, close_soup

        soup = open_soup(self.html)
        for img_tag in soup.find_all("img", attrs={"data-mirrored": "mirrored"}):
            img_tag["src"] = request.route_path("writeup_image", filename=img_tag["src"])
        html = close_soup(soup)
        return html

    def __repr__(self):
        return (
            "<WriteupPostVersion {self.id} of {self.writeup_post!r}: "
            "version {self.version}, active={self.active!r}>"
        ).format(self=self)


def likely_writeups(db_session, wpv):
    return (
        db_session.query(Writeup)
        .join(Writeup.posts)
        .filter(Writeup.status == "ongoing")
        .filter(WriteupPost.author == wpv.thread_post.author)
        .order_by(Writeup.id.desc())
    )


class FetchedImage(Base):
    # multiple original urls may map to the same id, unfortunately
    orig_url = Column(String, primary_key=True)
    id = Column(String(64), nullable=False)
