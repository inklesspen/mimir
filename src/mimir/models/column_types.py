import datetime
import uuid

import pytz
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator
import timeflake


class AwareDateTime(TypeDecorator):
    """
    A DateTime type which can only store tz-aware DateTimes
    """

    impl = DateTime(timezone=True)

    def process_bind_param(self, value, dialect):
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                raise ValueError("{!r} must be TZ-aware".format(value))
            else:
                value = value.astimezone(pytz.utc)
        return value

    def process_result_value(self, value, dialect):
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                value = pytz.utc.localize(value)
            else:
                value = value.astimezone(pytz.utc)
        return value

    def __repr__(self):
        return "AwareDateTime()"


class Timeflake(TypeDecorator):
    """
    A 128-bit, roughly-ordered, URL-safe UUID.
    """

    impl = UUID

    def process_bind_param(self, value, dialect):
        if isinstance(value, timeflake.Timeflake):
            return value.hex
        return value

    def process_result_value(self, value, dialect):
        if isinstance(value, str):
            value = uuid.UUID(hex=value)
        if isinstance(value, uuid.UUID):
            value = timeflake.parse(from_bytes=value.bytes)
        return value

    def __repr__(self):
        return "Timeflake()"

    @classmethod
    def generate(cls):
        return timeflake.random()
