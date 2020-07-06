import datetime

import pytz
from sqlalchemy import DateTime
from sqlalchemy.types import TypeDecorator


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
