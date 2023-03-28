import re

import pytz
import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
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

from .column_types import AwareDateTime, Timeflake
from .meta import Base


class Credential(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    cookies = Column(JSONB, nullable=False)
    timezone = Column(String(32), nullable=False)
    valid = Column(Boolean, nullable=False, default=sa.true())


class Thread(Base):
    # TODO: prevent a sequence from being made for this
    id = Column(Integer, primary_key=True)
    closed = Column(Boolean, nullable=False, default=False)
    # This should be actual page count, not merely the last fetched
    # 0 means we have not yet fetched anything
    page_count = Column(Integer, nullable=False)
    pages = relationship("ThreadPage", backref="thread")
    posts = relationship("ThreadPost", backref="thread", cascade_backrefs=False)

    pages_by_pagenum = relationship(
        "ThreadPage",
        collection_class=attribute_mapped_collection("page_num"),
        viewonly=True,
    )

    @property
    def url(self):
        return "https://forums.somethingawful.com/showthread.php?threadid={}".format(
            self.id
        )


class ThreadPage(Base):
    __table_args__ = (
        UniqueConstraint(
            "thread_id", "page_num", name="uq_thread_pages_thread_id_page_num"
        ),
    )
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    page_num = Column(Integer, nullable=False)
    html = Column(UnicodeText, nullable=False)
    last_fetched = Column(AwareDateTime, nullable=False)
    last_split = Column(AwareDateTime, nullable=True)
    fetched_with_id = Column(Integer, ForeignKey("credentials.id"), nullable=False)
    utc_offset_at_fetch = Column(Integer, nullable=True)
    # TODO: allow multiple fetches, generally only caring about the latest one
    # but keeping the rest around just in case?
    posts = relationship("ThreadPost", backref="page", order_by="ThreadPost.id")
    fetched_with = relationship("Credential", uselist=False)

    @property
    def url(self):
        return "{}&pagenumber={}".format(self.thread.url, self.page_num)

    @property
    def page_tz(self):
        if self.utc_offset_at_fetch is None:
            return pytz.timezone(self.fetched_with.timezone)
        # pytz.FixedOffset takes the offset in minutes, for some reason
        minutes = self.utc_offset_at_fetch / 60
        return pytz.FixedOffset(minutes)


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
    __table_args__ = (
        UniqueConstraint(
            "author_slug", "writeup_slug", name="uq_writeups_author_slug_writeup_slug"
        ),
        Index("collated_title", sa.column("title").collate("writeuptitle")),
    )
    id = Column(Integer, primary_key=True)
    author_slug = Column(String(100), nullable=False, index=True)
    writeup_slug = Column(String(100), nullable=False, index=True)
    title = Column(Unicode(100), nullable=False)
    author = Column(Unicode(100), nullable=False)
    status = Column(
        Enum(
            "ongoing", "abandoned", "completed", native_enum=False, name="check_status"
        ),
        nullable=False,
        index=True,
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
    author = Column(Unicode(40), nullable=False, index=True)
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

    changelog_entry = relationship(
        "ChangeLogWriteupEntry", uselist=False, back_populates="writeup_post"
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
        Index(
            "unattached_wpv",
            sa.column("id"),
            postgresql_where=sa.column("writeuppost_id") == sa.null(),
        ),
    )
    id = Column(Integer, primary_key=True)
    writeuppost_id = Column(
        Integer, ForeignKey("writeup_posts.id"), nullable=True, index=True
    )
    html = Column(UnicodeText, nullable=True)
    threadpost_id = Column(Integer, ForeignKey("thread_posts.id"), nullable=False)
    created_at = Column(AwareDateTime, nullable=False)

    version = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, nullable=False, default=False)

    url = association_proxy("thread_post", "url")

    def html_with_fixed_image_urls(self, request):
        from ..lib.extract import open_soup, close_soup

        soup = open_soup(self.html)
        for img_tag in soup.find_all("img", attrs={"data-mirrored": "mirrored"}):
            img_tag["src"] = request.route_path(
                "writeup_image", filename=img_tag["src"]
            )
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


class ChangeLogBatch(Base):
    __tablename__ = "change_log_batches"
    id = Column(Timeflake, primary_key=True, default=Timeflake.generate)
    created_at = Column(AwareDateTime, nullable=False, default=sa.func.now())

    generic_entries = relationship(
        "ChangeLogGenericEntry",
        backref="batch",
        cascade="all, delete-orphan",
        order_by="ChangeLogGenericEntry.created_at.asc()",
    )

    writeup_entries = relationship(
        "ChangeLogWriteupEntry",
        backref="batch",
        cascade="all, delete-orphan",
        order_by="ChangeLogWriteupEntry.created_at.asc()",
    )


class ChangeLogGenericEntry(Base):
    __tablename__ = "change_log_generic_entries"
    id = Column(Integer, primary_key=True)
    detail = Column(UnicodeText, nullable=False)
    created_at = Column(AwareDateTime, nullable=False, default=sa.func.now())
    changelogbatch_id = Column(
        Timeflake, ForeignKey("change_log_batches.id"), nullable=True
    )


class ChangeLogWriteupEntry(Base):
    __tablename__ = "change_log_writeup_entries"
    id = Column(Integer, primary_key=True)
    writeuppost_id = Column(Integer, ForeignKey("writeup_posts.id"), nullable=False)
    created_at = Column(AwareDateTime, nullable=False, default=sa.func.now())
    changelogbatch_id = Column(
        Timeflake, ForeignKey("change_log_batches.id"), nullable=True
    )

    writeup_post = relationship(
        "WriteupPost", uselist=False, back_populates="changelog_entry"
    )
