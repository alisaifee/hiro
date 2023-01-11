import datetime
import time

import pytest
import six

from hiro.errors import InvalidTypeError
from hiro.utils import chained, time_in_seconds, timedelta_to_seconds, utc


def test_fractional():
    delta = datetime.timedelta(seconds=1, microseconds=1000)
    assert round(abs(timedelta_to_seconds(delta) - 1.001), 7) == 0


def test_days():
    delta = datetime.timedelta(days=10)
    assert timedelta_to_seconds(delta) == delta.days * 24 * 60 * 60


def test_passthrough():
    assert time_in_seconds(1) == 1

    long_instance = long(1) if six.PY2 else 1  # noqa: F821
    assert time_in_seconds(long_instance) == long_instance
    assert time_in_seconds(1.0) == 1.0


def test_date():
    d = datetime.date(1970, 1, 1)
    assert time_in_seconds(d) == 0

    d = d + datetime.timedelta(days=1234)
    assert time_in_seconds(d) == 1234 * 24 * 60 * 60


def test_datetime():
    d = datetime.datetime(1970, 1, 1, 0, 0, 0)
    assert time_in_seconds(d) == time.mktime(d.timetuple())


def test_tzaware_datetime():
    d = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=utc)
    assert time_in_seconds(d) == 0


def test_invalid_type():
    with pytest.raises(InvalidTypeError):
        time_in_seconds("this is a string")


class TestChained(object):
    class Foo(object):
        @chained
        def return_value(self, value=None):
            return value

    def setup_method(self):
        self.obj = self.Foo()

    def test_no_return(self):
        assert self.obj.return_value() is self.obj

    def test_with_return(self):
        o = object()
        assert self.obj.return_value(o) is o

    def test_kwargs(self):
        o = object()
        assert self.obj.return_value(value=o) is o
