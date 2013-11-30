import functools
from .core import ScaledAsyncRunner, ScaledRunner, ScaledTimeline, Timeline


# module exports
run_sync = ScaledRunner
run_async = ScaledAsyncRunner
scaled_timeline = functools.partial(ScaledTimeline, segment=None)

