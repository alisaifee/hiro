import datetime
import six
import unittest

import hiro
from hiro.errors import InvalidTypeError
from hiro.utils import timedelta_to_seconds, time_in_seconds, chained


class TestTimeDeltaToSeconds(unittest.TestCase):
    def test_fractional(self):
        delta = datetime.timedelta(seconds=1, microseconds=1000)
        self.assertAlmostEqual(timedelta_to_seconds(delta), 1.001)

    def test_days(self):
        delta = datetime.timedelta(days=10)
        self.assertEqual(timedelta_to_seconds(delta),
                         delta.days * 24 * 60 * 60)


class TestTimeInSeconds(unittest.TestCase):
    def test_passthrough(self):
        self.assertEqual(time_in_seconds(1), 1)

        long_instance = long(1) if six.PY2 else 1
        self.assertEqual(time_in_seconds(long_instance), long_instance)
        self.assertEqual(time_in_seconds(1.0), 1.0)

    def test_date(self):
        d = datetime.date(1970, 1, 1)
        self.assertEqual(time_in_seconds(d), 0)

    def test_datetime(self):
        d = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.assertEqual(time_in_seconds(d), 0)

    def test_invalid_type(self):
        self.assertRaises(
            InvalidTypeError, time_in_seconds, "this is a string")


class TestChained(unittest.TestCase):
    class Foo(object):
        @chained
        def return_value(self, value=None):
            return value

    def setUp(self):
        self.obj = self.Foo()

    def test_no_return(self):
        self.assertTrue(self.obj.return_value() is self.obj)

    def test_with_return(self):
        o = object()
        self.assertTrue(self.obj.return_value(o) is o)

    def test_kwargs(self):
        o = object()
        self.assertTrue(self.obj.return_value(value=o) is o)
