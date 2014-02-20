"""
timeline & runner implementation
"""

import sys
import threading
import time
import datetime
from six import reraise

if sys.version_info >= (3, 0, 0):
    from contextlib import ContextDecorator #pragma: no cover
else:
    from contextdecorator import ContextDecorator #pragma: no cover

import mock
from .errors import SegmentNotComplete, TimeOutofBounds
from .utils import timedelta_to_seconds, chained, time_in_seconds
from .patches import Date, Datetime

BLACKLIST = set()

class Segment(object):
    """
    utility class to manager execution result and timings
    for :class:`SyncRunner
    """

    def __init__(self):
        self.__error = False
        self.__response = None
        self.__start = time.time()
        self.__end = None

    def complete(self, response):
        """
        called upon successful completion of the segment
        """
        self.__response = response

    def complete_with_error(self, exception):
        """
        called if the segment errored during execution
        """
        self.__error = exception

    @property
    def complete_time(self):
        """
        returns the completion time
        """
        return self.__end

    @complete_time.setter
    def complete_time(self, completion_time):
        """
        sets the completion time
        """
        self.__end = completion_time

    @property
    def start_time(self):
        """
        returns the start time
        """
        return self.__start

    @start_time.setter
    def start_time(self, start_time):
        """
        sets the start time
        """
        self.__start = start_time

    @property
    def runtime(self):
        """
        returns the total execution time of the segment
        """
        if self.__end:
            return self.complete_time - self.start_time
        else:
            raise SegmentNotComplete

    @property
    def response(self):
        """
        returns the return value captured in the segment or raises
        the :exception:`exceptions.Exception` that was caught.
        """
        if not self.__end:
            raise SegmentNotComplete
        else:
            if self.__error:
                reraise(self.__error[0], self.__error[1], self.__error[2])
            return self.__response

class Timeline(ContextDecorator):
    """
    Timeline context manager. Within this context
    the builtins :func:`time.time`, :func:`time.sleep`,
    :meth:`datetime.datetime.now`, :meth:`datetime.date.today`,
    :meth:`datetime.datetime.utcnow` and :func:`time.gmtime`
    respect the alterations made to the timeline.

    The class can be used either as a context manager or a decorator.

    The following are all valid ways to use it.

    .. code-block:: python

        with Timeline(scale=10, start=datetime.datetime(2012,12,12)):
            ....

        fast_timeline = Timeline(scale=10).forward(120)

        with fast_timeline as timeline:
            ....

        delta = datetime.date(2015,1,1) - datetime.date.today()
        future_frozen_timeline = Timeline(scale=10000).freeze().forward(delta)
        with future_frozen_timeline as timeline:
            ...

        @Timeline(scale=100)
        def slow():
            time.sleep(120)


    :param float scale: > 1 time will go faster and < 1 it will be slowed down.
    :param start: if specified starts the timeline at the given value (either a
        floating point representing seconds since epoch or a
        :class:`datetime.datetime` object)

    """

    class_mappings = {
        "date": (datetime.date, Date),
        "datetime": (datetime.datetime, Datetime)
    }

    def __init__(self, scale=1, start=None):
        self.reference = time.time()
        self.offset = time_in_seconds(start) - self.reference if start else 0.0
        self.freeze_point = self.freeze_at = None
        self.patchers = []
        self.mock_mappings = {
            "datetime.date": (datetime.date, Date),
            "datetime.datetime": (datetime.datetime, Datetime),
            "time.time": (time.time, self.__time_time),
            "time.sleep": (time.sleep, self.__time_sleep),
            "time.gmtime": (time.gmtime, self.__time_gmtime)
        }
        self.factor = scale

    def _get_original(self, fn_or_mod):
        """
        returns the original moduel or function
        """
        if fn_or_mod in self.mock_mappings:
            return self.mock_mappings[fn_or_mod][0]
        else:
            return self.class_mappings[fn_or_mod][0]

    def _get_fake(self, fn_or_mod):
        """
        returns the mocked/patched module or function
        """
        if fn_or_mod in self.mock_mappings:
            return self.mock_mappings[fn_or_mod][1]
        else:
            return self.class_mappings[fn_or_mod][1]

    def __compute_time(self, freeze_point, offset):
        """
        computes the current_time after accounting for
        any adjustments due to :attr:`factor` or invocations
        of :meth:`freeze`, :meth:`rewind` or :meth:`forward`
        """
        if not freeze_point is None:
            return offset + freeze_point
        else:
            delta = self._get_original("time.time")() - self.reference
            return self.reference + (delta * self.factor) + offset

    def __check_out_of_bounds(self, offset=None, freeze_point=None):
        """
        ensures that the time that would be calculated based on any
        offset or freeze point would not result in jumping beyond the epoch
        """
        next_time = self.__compute_time(freeze_point or self.freeze_point,
                                      offset or self.offset
        )
        if next_time < 0:
            raise TimeOutofBounds(next_time)

    def __time_time(self):
        """
        patched version of :func:`time.time`
        """
        return self.__compute_time(self.freeze_point, self.offset)

    def __time_gmtime(self, seconds=None):
        """
        patched version of :func:`time.gmtime`
        """
        return self._get_original("time.gmtime")(seconds or self.__time_time())

    def __time_sleep(self, amount):
        """
        patched version of :func:`time.sleep`
        """
        self._get_original("time.sleep")(1.0 * amount / self.factor)

    @chained
    def forward(self, amount):
        """
        forwards the timeline by the specified :attr:`amount`

        :param amount: either an integer representing seconds or
         a :class:`datetime.timedelta` object
        """
        offset = self.offset
        if isinstance(amount, datetime.timedelta):
            offset += timedelta_to_seconds(amount)
        else:
            offset += amount
        self.__check_out_of_bounds(offset=offset)
        self.offset = offset

    @chained
    def rewind(self, amount):
        """
        rewinds the timeline by the specified :attr:`amount`

        :param amount: either an integer representing seconds or
         a :class:`datetime.timedelta` object
        """
        offset = self.offset
        if isinstance(amount, datetime.timedelta):
            offset -= timedelta_to_seconds(amount)
        else:
            offset -= amount
        self.__check_out_of_bounds(offset=offset)
        self.offset = offset

    @chained
    def freeze(self, target_time=None):
        """
        freezes the timeline

        :param target_time: the time to freeze at as either a float representing
            seconds since the epoch or a :class:`datetime.datetime` object.
            If not provided time will be frozen at the current time of the
            enclosing :class:`Timeline`
        """
        if target_time is None:
            freeze_point = self._get_fake("time.time")()
        else:
            freeze_point = time_in_seconds(target_time)
        self.__check_out_of_bounds(freeze_point=freeze_point)
        self.freeze_point = freeze_point
        self.offset = 0

    @chained
    def unfreeze(self):
        """
        if a call to :meth:`freeze` was previously made, the timeline will be
        unfrozen to the point which :meth:`freeze` was invoked.

        .. warning::

            Since unfreezing will reset the timeline back to the point in
            when the :meth:`freeze` was invoked - the effect of previous
            invocations of :meth:`forward` and :meth:`rewind` will
            be lost. This is by design so that freeze/unfreeze can be used as
            a checkpoint mechanism.

        """
        if self.freeze_point is not None:
            self.reference = self._get_original("time.time")()
            self.offset = time_in_seconds(self.freeze_point) - self.reference
            self.freeze_point = None


    @chained
    def scale(self, factor):
        """
        changes the speed at which time elapses and how long sleeps last for.

        :param float factor: > 1 time will go faster and < 1 it will be slowed
            down.

        """
        self.factor = factor
        self.reference = self._get_original("time.time")()

    @chained
    def reset(self):
        """
        resets the current timeline to the actual time now
        with a scale factor 1
        """

        self.factor = 1
        self.freeze_point = None
        self.reference = self._get_original("time.time")()
        self.offset = 0

    def __enter__(self):
        for name, module in sys.modules.items():
            if module in BLACKLIST:
                continue
            for kls in self.class_mappings:
                try:
                    if kls in dir(module) and getattr(module,
                                                  kls) == self._get_original(
                        kls):
                        path = "%s.%s" % (name, kls)
                        if not path in self.mock_mappings:
                            patcher = mock.patch(path, self._get_fake(kls))
                            self.patchers.append(patcher)
                            patcher.start()
                # this is done for cases where invalid modules are on
                # sys modules.
                # pylint: disable=bare-except
                except:
                    BLACKLIST.add(module)
        for time_obj in self.mock_mappings:
            patcher = mock.patch(time_obj, self._get_fake(time_obj))
            self.patchers.append(patcher)
            patcher.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for patcher in self.patchers:
            patcher.stop()
        self.patchers = []


class ScaledRunner(object):
    """
    manages the execution of a callable within a :class:`hiro.Timeline`
    context.
    """
    def __init__(self, factor, func, *args, **kwargs):
        self.func = func
        self.func_args = args
        self.func_kwargs = kwargs
        self.segment = Segment()
        self.factor = factor
        self.__call__()

    def _run(self):
        """
        managed execution of :attr:`func`
        """
        self.segment.start_time = time.time()
        with Timeline(scale=self.factor):
            try:
                self.segment.complete(
                    self.func(*self.func_args, **self.func_kwargs))
            # will be rethrown
            # pylint: disable=bare-except
            except:
                self.segment.complete_with_error(sys.exc_info())
        self.segment.complete_time = time.time()

    def __call__(self):
        self._run()
        return self

    def get_response(self):
        """
        :returns: the return value from :attr:`func`
        :raises: Exception if the :attr:`func` raised one during execution
        """
        return self.segment.response


    def get_execution_time(self):
        """
        :returns: the real execution time of :attr:`func` in seconds
        """
        return self.segment.runtime


class ScaledAsyncRunner(ScaledRunner):
    """
    manages the asynchronous execution of a callable within a
    :class:`hiro.Timeline` context.
    """
    def __init__(self, *args, **kwargs):
        self.thread_runner = threading.Thread(target=self._run)
        super(ScaledAsyncRunner, self).__init__(*args, **kwargs)

    def __call__(self):
        self.thread_runner.start()
        return self

    def is_running(self):
        """
        :rtype bool: whether the :attr:`func` is still running or not.
        """
        return self.thread_runner.is_alive()

    def join(self):
        """
        waits for the :attr:`func` to complete execution.
        """
        return self.thread_runner.join()


def run_sync(factor, func, *args, **kwargs):
    """
    Executes a callable within a :class:`hiro.Timeline`

    :param int factor: scale factor to use for the timeline during execution
    :param function func: the function to invoke
    :param args: the arguments to pass to the function
    :param kwargs: the keyword arguments to pass to the function
    :returns: an instance of :class:`hiro.core.ScaledRunner`

    """
    return ScaledRunner(factor, func, *args, **kwargs)

def run_async(factor, func, *args, **kwargs):
    """
    Asynchronously executes a callable within a :class:`hiro.Timeline`

    :param int factor: scale factor to use for the timeline during execution
    :param function func: the function to invoke
    :param args: the arguments to pass to the function
    :param kwargs: the keyword arguments to pass to the function
    :returns: an instance of :class:`hiro.core.ScaledAsyncRunner`

    """
    return ScaledAsyncRunner(factor, func, *args, **kwargs)
