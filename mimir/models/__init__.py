# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re
import datetime
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    String,
    Boolean,
    ForeignKey,
    UnicodeText,
    UniqueConstraint,
    Unicode,
    Enum,
    CheckConstraint,
    )

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.types import TypeDecorator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from zope.sqlalchemy import register
import transaction


class Base(object):
    @declared_attr
    def __tablename__(cls):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return name + "s"

Base = declarative_base(cls=Base)


class AwareDateTime(TypeDecorator):
    """
    A DateTime type which can only store tz-aware DateTimes
    """
    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            raise ValueError("{!r} must be TZ-aware".format(value))
        return value

    def __repr__(self):
        return 'AwareDateTime()'


class Credential(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    cookies = Column(JSONB, nullable=False)
    timezone = Column(String(32), nullable=False)
    valid = Column(Boolean, nullable=False, default=sa.true())


class AuditEntry(Base):
    __tablename__ = 'audit_entries'
    id = Column(Integer, primary_key=True)
    credential_id = Column(Integer, ForeignKey('credentials.id'), nullable=False)
    text = Column(Unicode, nullable=False)
    timestamp = Column(AwareDateTime, nullable=False)


class Thread(Base):
    # TODO: prevent a sequence from being made for this
    id = Column(Integer, primary_key=True)
    closed = Column(Boolean, nullable=False, default=False)
    # This should be actual page count, not merely the last fetched
    # 0 means we have not yet fetched anything
    page_count = Column(Integer, nullable=False)
    pages = relationship("ThreadPage", backref="thread")
    posts = relationship("ThreadPost", backref="thread")

    @property
    def url(self):
        return "http://forums.somethingawful.com/showthread.php?threadid={}".format(self.id)


class ThreadPage(Base):
    __table_args__ = (UniqueConstraint("thread_id", "page_num"),)
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    page_num = Column(Integer, nullable=False)
    html = Column(UnicodeText, nullable=False)
    last_fetched = Column(AwareDateTime, nullable=False)
    last_split = Column(AwareDateTime, nullable=True)
    fetched_with_id = Column(Integer, ForeignKey("credentials.id"), nullable=False)
    posts = relationship("ThreadPost", backref="page")
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

    @property
    def url(self):
        return "{}#post{}".format(self.page.url, self.id)


class Writeup(Base):
    __table_args__ = (UniqueConstraint("author_slug", "writeup_slug"),)
    id = Column(Integer, primary_key=True)
    author_slug = Column(String(100), nullable=False, index=True)
    writeup_slug = Column(String(100), nullable=False, index=True)
    title = Column(Unicode(100), nullable=False)
    status = Column(Enum('ongoing', 'abandoned', 'completed', native_enum=False), nullable=False)
    published = Column(Boolean, nullable=False, default=False)
    # anything with offensive_content will be blocked in robots.txt
    # this is for reviews of stuff that is unredeemable shit
    offensive_content = Column(Boolean, nullable=False, default=False)
    # this is for reviews of stuff that respectfully handle triggery shit
    triggery_content = Column(Boolean, nullable=False, default=False)

    posts = relationship("WriteupPost", backref="writeup", order_by='WriteupPost.index')

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

    versions = relationship("WriteupPostVersion", backref="writeup_post")


class WriteupPostVersion(Base):
    __table_args__ = (
        CheckConstraint(sa.or_(sa.column('writeuppost_id') != sa.null(), sa.column('active') == sa.false())),
        )
    id = Column(Integer, primary_key=True)
    writeuppost_id = Column(Integer, ForeignKey("writeup_posts.id"), nullable=True)
    html = Column(UnicodeText, nullable=True)
    threadpost_id = Column(Integer, ForeignKey("thread_posts.id"), nullable=False)
    created_at = Column(AwareDateTime, nullable=False)

    version = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, nullable=False, default=False)

    edit_summary = Column(Unicode(200), nullable=False)


class FetchedImage(Base):
    # multiple original urls may map to the same id, unfortunately
    orig_url = Column(String, primary_key=True)
    id = Column(String(64), nullable=False)


def create_session(request):
    sessionmaker = request.registry['db_sessionmaker']
    session = sessionmaker()
    register(session, transaction_manager=request.tm)
    return session


def pyramid_tm_hook(request=None):
    return transaction.TransactionManager()


def includeme(config):
    config.add_settings({'tm.manager_hook': pyramid_tm_hook})
    settings = config.get_settings()
    config.include('pyramid_tm')
    engine = engine_from_config(settings, 'sqlalchemy.')
    maker = sessionmaker()
    maker.configure(bind=engine)
    config.registry['db_sessionmaker'] = maker
    config.add_request_method(create_session, 'db_session', reify=True)
