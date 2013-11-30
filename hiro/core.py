"""

"""
import sys
import threading
import time
import datetime
import contextdecorator
import mock
from .errors import SegmentNotComplete, TimeOutofBounds
from .patches import Date, Datetime


class Segment(object):
    def __init__(self):
        self.__error = False
        self.__response = None
        self.__start = time.time()
        self.__end = None

    def complete(self, response):
        self.__response = response

    def complete_with_error(self, exception):
        self.__error = exception

    @property
    def complete_time(self):
        return self.__end

    @complete_time.setter
    def complete_time(self, time):
        self.__end = time

    @property
    def start_time(self):
        return self.__start

    @start_time.setter
    def start_time(self, time):
        self.__start = time

    @property
    def runtime(self):
        if self.__end:
            return self.complete_time - self.start_time
        else:
            raise SegmentNotComplete

    @property
    def response(self):
        if not self.__end:
            raise SegmentNotComplete
        else:
            if self.__error:
                raise self.__error[0], self.__error[1], self.__error[2]
            return self.__response

class Timeline(object):
    def __init__(self):
        self.reference = time.time()
        self.reference_gmtime = time.mktime(time.gmtime())
        self.factor = 1
        self.offset = 0.0
        self.freeze_point = self.freeze_at = None
        self.freeze_offset = 0
        self.patchers = []
        self.mock_mappings = {
            "datetime.date": (datetime.date, Date),
            "datetime.datetime": (datetime.datetime, Datetime),
            "time.time": (time.time, self.time_time),
            "time.sleep": (time.sleep, self.time_sleep),
            "time.gmtime": (time.gmtime, self.time_gmtime)
        }
        self.class_mappings = {
            "date": (datetime.date, Date),
            "datetime": (datetime.datetime, Datetime)
        }

        # start fake time methods

    def get_original(self, fn_or_mod):
        return (self.mock_mappings if self.mock_mappings.has_key(fn_or_mod) else self.class_mappings)[fn_or_mod][0]

    def get_fake(self, fn_or_mod):
        return (self.mock_mappings if self.mock_mappings.has_key(fn_or_mod) else self.class_mappings)[fn_or_mod][1]

    def compute_time(self, freeze_point, offset):
        if not freeze_point is None:
            return (offset * self.factor) + freeze_point
        else:
            delta = self.get_original("time.time")() - self.reference
            return self.reference + (delta * self.factor) + offset  - self.freeze_offset

    def check_out_of_bounds(self, offset=None, freeze_point=None):
        next_time = self.compute_time(freeze_point or self.freeze_point, offset or self.offset)
        if next_time < 0:
            raise TimeOutofBounds(next_time)

    def time_time(self):
        return self.compute_time(self.freeze_point, self.offset)

    def time_gmtime(self, seconds=None):
        return self.get_original("time.gmtime")(seconds or self.time_time())

    def time_sleep(self, amount):
        self.get_original("time.sleep")(1.0 * amount / self.factor)


    def forward(self, amount):
        offset = self.offset
        if isinstance(amount, datetime.timedelta):
            offset += (amount.microseconds + (amount.seconds + amount.days * 24 * 3600) * 10**6) / 10**6
        else:
            offset += amount
        self.check_out_of_bounds(offset=offset)
        self.offset = offset

    def rewind(self, amount):
        offset = self.offset
        if isinstance(amount, datetime.timedelta):
            offset -= (amount.microseconds + (
            amount.seconds + amount.days * 24 * 3600) * 10 ** 6) / 10 ** 6
        else:
            offset -= amount
        self.check_out_of_bounds(offset=offset)
        self.offset = offset

    def freeze(self, at=None):
        if at is None:
            freeze_point = self.get_fake("time.time")()
        else:
            if isinstance(at, (self.get_original("datetime.date"),
                               self.get_original("datetime.datetime"))):
                freeze_point = time.mktime(at.timetuple())
            elif isinstance(at, (float, int)):
                freeze_point = at
            else:
                raise AttributeError(
                    "freeze accepts a float/int (time since epoch), datetime or"
                    "date objects as freeze points. You provided a %s" % (
                    type(at)
                    )
                )
        self.check_out_of_bounds(freeze_point=freeze_point)
        self.freeze_point = freeze_point
        self.freeze_at = self.get_original("time.time")()

    def unfreeze(self):
        if self.freeze_point is not None:
            self.freeze_offset =  self.reference - self.freeze_point
            self.reference = self.freeze_at
            self.freeze_at = None
            self.freeze_point = None


    def scale(self, factor):
        self.factor = factor

    def reset(self):
        self.factor = 1
        self.freeze_offset = 0
        self.freeze_point = None
        self.reference = self.get_original("time.time")()
        self.offset = 0

    def __enter__(self):
        for name, module in sys.modules.items():
            for kls in self.class_mappings:
                if kls in dir(module) and getattr(module, kls) == self.get_original(kls):
                    path = "%s.%s" % (name, kls)
                    if not path in self.mock_mappings:
                        patcher = mock.patch(path, self.get_fake(kls))
                        self.patchers.append(patcher)
                        patcher.start()

        for time_obj in self.mock_mappings:
            patcher = mock.patch(time_obj, self.get_fake(time_obj))
            self.patchers.append(patcher)
            patcher.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for patcher in self.patchers:
            patcher.stop()
        self.patchers = []

class ScaledTimeline(Timeline, contextdecorator.ContextDecorator):
    def __init__(self, factor=1, segment=None):
        self.segment = segment
        super(ScaledTimeline, self).__init__()
        self.factor = factor

    def __enter__(self):
        if self.segment:
            self.segment.start_time = self.get_original("time.time")()
        return super(ScaledTimeline, self).__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return super(ScaledTimeline, self).__exit__(exc_type, exc_value, traceback)


class ScaledRunner(object):
    def __init__(self, factor, callable, *args, **kwargs):
        self.callable = callable
        self.callable_args = args
        self.callable_kwargs = kwargs
        self.segment = Segment()
        self.factor = factor
        self.__call__()

    def run(self):
        with ScaledTimeline(self.factor, self.segment):
            try:
                self.segment.complete(self.callable(*self.callable_args, **self.callable_kwargs))
            except Exception, e:
                self.segment.complete_with_error(sys.exc_info())
        self.segment.complete_time = time.time()

    def __call__(self):
        self.run()
        return self

    def get_response(self):
        return self.segment.response


    def get_execution_time(self):
        return self.segment.runtime


class ScaledAsyncRunner(ScaledRunner):
    def __call__(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        return self

    def is_running(self):
        return self.thread.is_alive()

    def join(self):
        return self.thread.join()


