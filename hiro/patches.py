"""
patched builtin time classes for use by :class:`hiro.Timeline`
"""
import abc
import time
from datetime import date as realdate
from datetime import datetime as realdatetime


class DatetimeMeta(abc.ABCMeta):
    """
    meta class to allow interaction between :class:`datetime.datetime`
    objects create inside the :class:`hiro.Timeline` with those created
    outside it.
    """

    def __instancecheck__(cls, instance):
        return isinstance(instance, realdatetime)


class DateMeta(type):
    """
    meta class to allow interaction between :class:`datetime.date`
    objects create inside the :class:`hiro.Timeline` with those created
    outside it.
    """

    def __instancecheck__(cls, instance):
        return isinstance(instance, realdate)


class Datetime(realdatetime, metaclass=DatetimeMeta):
    """
    used to patch :class:`datetime.datetime` to follow the rules of the
    parent :class:`hiro.Timeline`
    """

    @classmethod
    def now(cls, tz=None):
        return cls.fromtimestamp(time.time(), tz)

    @classmethod
    def utcnow(cls):
        return cls.utcfromtimestamp(time.time())


class Date(realdate, metaclass=DateMeta):
    """
    used to patch :class:`datetime.date` to follow the rules of the
    parent :class:`hiro.Timeline`
    """

    __metaclass__ = DateMeta

    @classmethod
    def today(cls):
        return cls.fromtimestamp(time.time())
