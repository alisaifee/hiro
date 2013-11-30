"""

"""
import datetime
import time

class Datetime(datetime.datetime):
    @classmethod
    def now(clz, tz=None):
        return datetime.datetime.fromtimestamp(time.time(), tz)


class Date(datetime.date):
    @classmethod
    def today(cls):
        return datetime.date.fromtimestamp(time.time())
