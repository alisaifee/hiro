"""
patched builtin time classes for use by :class:`hiro.Timeline`
"""
import datetime
import time

class Datetime(datetime.datetime):
    """
    used to patch :class:`datetime.datetime` to follow the rules of the
    parent :class:`hiro.Timeline`
    """
    @classmethod
    def now(cls, tz=None):
        return datetime.datetime.fromtimestamp(time.time(), tz)

    @classmethod
    def utcnow(cls):
        return datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))

class Date(datetime.date):
    """
    used to patch :class:`datetime.date` to follow the rules of the
    parent :class:`hiro.Timeline`
    """
    @classmethod
    def today(cls):
        return datetime.date.fromtimestamp(time.time())

