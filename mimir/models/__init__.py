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
    Enum
    )

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.types import TypeDecorator
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from zope.sqlalchemy import register


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
    id = Column(Integer, primary_key=True)
    closed = Column(Boolean, nullable=False, default=False)
    # This should be actual page count, not merely the last fetched
    # 0 means we have not yet fetched anything
    page_count = Column(Integer, nullable=False)
    pages = relationship("ThreadPage", backref="thread")
    posts = relationship("ThreadPost", backref="thread")


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


class ThreadPost(Base):
    id = Column(Integer, primary_key=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("thread_pages.id"), nullable=False)
    author = Column(Unicode(40), nullable=False)
    timestamp = Column(AwareDateTime, nullable=False)
    html = Column(UnicodeText, nullable=False)
    last_extracted = Column(AwareDateTime, nullable=False)


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

    posts = relationship("WriteupPost", backref="writeup", order_by='WriteupPost.ordinal')


class WriteupPost(Base):
    id = Column(Integer, primary_key=True)
    writeup_id = Column(Integer, ForeignKey("writeups.id"), nullable=False)
    author = Column(Unicode(40), nullable=False)
    index = Column(Integer, nullable=False)
    # Some posts have 1.5 and so on, but I don't want to use floats
    ordinal = Column(Unicode(5), nullable=False)
    title = Column(Unicode, nullable=True)
    url = Column(Unicode, nullable=False)
    last_fetched = Column(AwareDateTime, nullable=False)

    versions = relationship("WriteupPostVersion", backref="writeup_post")


class WriteupPostVersion(Base):
    id = Column(Integer, primary_key=True)
    writeuppost_id = Column(Integer, ForeignKey("writeup_posts.id"), nullable=False)
    html = Column(UnicodeText, nullable=False)
    threadpost_id = Column(Integer, ForeignKey("thread_posts.id"), nullable=True)
    extracted_at = Column(AwareDateTime, nullable=False)


class Image(Base):
    id = Column(String(64), primary_key=True)
    size = Column(ARRAY(Integer), nullable=False)


def includeme(config):
    settings = config.get_settings()
    config.include('pyramid_tm')
    engine = engine_from_config(settings, 'sqlalchemy.')
    maker = sessionmaker()
    register(maker)
    maker.configure(bind=engine)
    config.registry['db_sessionmaker'] = sessionmaker
    config.add_request_method(lambda request: maker(), 'db_session', reify=True)
