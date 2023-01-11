"""
random utility functions
"""
import calendar
import datetime
import functools
import time

from .errors import InvalidTypeError

utc = datetime.timezone.utc


def timedelta_to_seconds(delta):
    """
    converts a timedelta object to seconds
    """
    seconds = delta.microseconds
    seconds += (delta.seconds + delta.days * 24 * 3600) * 10**6
    return float(seconds) / 10**6


def time_in_seconds(value):
    """
    normalized either a datetime.date, datetime.datetime or float
    to a float corresponding to a UTC timestamp.

    datetime.date objects are converted to the timestamp of midnight UTC on
    that date.

    Naive datetime objects (without timezone information) are taken in the
    local timezone.
    """
    if isinstance(value, (float, int)):
        return value
    elif isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            return time.mktime(value.timetuple())
        else:
            return calendar.timegm(value.astimezone(utc).timetuple())
    elif isinstance(value, datetime.date):
        # We're really explicit here but we could just use value.timetuple()
        return calendar.timegm(
            datetime.datetime.combine(value, datetime.time(0, 0, 0, 0, utc)).timetuple()
        )
    else:
        raise InvalidTypeError(value)


def chained(method):
    """
    Method decorator to allow chaining.

    adopted from:
    http://www.snip2code.com/Snippet/2535/Fluent-interface-decorators
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        fluent wrapper
        """
        result = method(self, *args, **kwargs)
        return self if result is None else result

    return wrapper
