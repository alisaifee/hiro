"""
random utility functions
"""
import datetime
import functools
import time
from .errors import InvalidTypeError


def timedelta_to_seconds(delta):
    """
    converts a timedelta object to seconds
    """
    seconds = delta.microseconds
    seconds += (delta.seconds + delta.days * 24 * 3600) * 10 ** 6
    return float(seconds) / 10 ** 6



def time_in_seconds(value):
    """
    normalized either a datetime.date, datetime.datetime or float
    to a float corresponding to a UTC timestamp.

    Naive datetime objects (without timezone information) are taken in the
    local timezone.
    """
    if isinstance(value, (float, int)):
        return value
    elif isinstance(value, (datetime.date, datetime.datetime)):
        return time.mktime(value.timetuple())
    else:
        raise InvalidTypeError(value)

#adopted from: http://www.snip2code.com/Snippet/2535/Fluent-interface-decorators

def chained(method):
    """
    Method decorator to allow chaining.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        fluent wrapper
        """
        result = method(self, *args, **kwargs)
        return self if result is None else result
    return wrapper
