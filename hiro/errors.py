"""
exceptions used by hiro.
"""


class SegmentNotComplete(Exception):
    """
    used to raise an exception if an async segment hasn't completed yet
    """


class TimeOutofBounds(AttributeError):
    """
    used to raise an exception when time is rewound beyond the epoch
    """

    def __init__(self, oob_time):
        message = (
            "you've frozen time at a point before the epoch (%d)."
            "hiro only supports going back to 1970/01/01 07:30:00" % oob_time
        )
        super().__init__(message)


class InvalidTypeError(TypeError):
    """
    used to raise an exception when an invalid type is provided
    for type operations
    """

    def __init__(self, value):
        message = (
            "%s provided when only float, int, datetime, or date objects"
            "are supported" % type(value)
        )
        super().__init__(message)
