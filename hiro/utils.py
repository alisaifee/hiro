"""
random utility functions
"""


def timedelta_to_seconds(delta):
    """
    converts a timedelta object to seconds
    """
    seconds = delta.microseconds
    seconds += (delta.seconds + delta.days * 24 * 3600) * 10 ** 6
    return seconds / 10 ** 6
