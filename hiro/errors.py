"""

"""


class SegmentNotComplete(Exception):
    """
    used to raise an exception if an async segment hasn't completed yet
    """
    pass


class TimeOutofBounds(AttributeError):
    """
    used to raise an exception when time is rewound beyond the epoch
    """
    def __init__(self, oob_time):
        message = "you've frozen time at a point before the epoch (%d).. hiro can't compute" % oob_time
        super(TimeOutofBounds, self).__init__(message)



