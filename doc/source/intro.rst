**********************************
Hiro context manager and utilities
**********************************

Timeline context
================
The :class:`~hiro.Timeline` context manager hijacks a few commonly used time functions
to allow time manipulation within its context. Specifically :func:`~time.sleep`, :func:`~time.time`, :func:`time.time_ns`,
:func:`~time.monotonic`, :func:`time.monotonic_ns`, :func:`time.localtime`, :func:`~time.gmtime`,
:meth:`datetime.datetime.now`, :meth:`datetime.datetime.utcnow` and :meth:`datetime.datetime.today`
behave according the configuration of the context.

The context provides the following manipulation options:

* :meth:`~hiro.Timeline.rewind`: accepts seconds as an integer or an :class:`~datetime.timedelta` instance.
* :meth:`~hiro.Timeline.forward`: accepts seconds as an integer or an :class:`~datetime.timedelta` instance.
* :meth:`~hiro.Timeline.freeze`: accepts a floating point time since epoch or a :class:`~datetime.datetime` or :class:`~datetime.date` instance to freeze the time at.
* :meth:`~hiro.Timeline.unfreeze`: resumes time from the point it was frozen at.
* :meth:`~hiro.Timeline.scale`: accepts a floating point to accelerate/decelerate time by. ``> 1 = acceleration,  < 1 = deceleration``
* :meth:`~hiro.Timeline.reset`: resets all time alterations.

.. code-block:: python

    import hiro
    from datetime import timedelta, datetime
    import time

    datetime.now().isoformat()
    # OUT: '2013-12-01T06:55:41.706060'
    with hiro.Timeline() as timeline:

        # forward by an hour
        timeline.forward(60*60)
        datetime.now().isoformat()
        # OUT: '2013-12-01T07:55:41.707383'

        # jump forward by 10 minutes
        timeline.forward(timedelta(minutes=10))
        datetime.now().isoformat()
        # OUT: '2013-12-01T08:05:41.707425'

        # jump to yesterday and freeze
        timeline.freeze(datetime.now() - timedelta(hours=24))
        datetime.now().isoformat()
        # OUT: '2013-11-30T09:15:41'

        timeline.scale(5) # scale time by 5x
        time.sleep(5) # this will effectively only sleep for 1 second

        # since time is frozen the sleep has no effect
        datetime.now().isoformat()
        # OUT: '2013-11-30T09:15:41'

        timeline.rewind(timedelta(days=365))

        datetime.now().isoformat()
        # OUT: '2012-11-30T09:15:41'



To reduce the amount of statements inside the context, certain timeline setup
tasks can be done via the constructor and/or by using the fluent interface.



.. code-block:: python

    import hiro
    import time
    from datetime import timedelta, datetime

    start_point = datetime(2012,12,12,0,0,0)
    my_timeline = hiro.Timeline(scale=5).forward(60*60).freeze()
    with my_timeline as timeline:
        print datetime.now()
        # OUT: '2012-12-12 01:00:00.000315'
        time.sleep(5) # effectively 1 second
        # no effect as time is frozen
        datetime.now()
        # OUT: '2012-12-12 01:00:00.000315'
        timeline.unfreeze()
        # back to starting point
        datetime.now()
        # OUT: '2012-12-12 01:00:00.000317'
        time.sleep(5) # effectively 1 second
        # takes effect (+5 seconds)
        datetime.now()
        # OUT: '2012-12-12 01:00:05.003100'


:class:`~hiro.Timeline` can additionally be used as a decorator. If the decorated
function expects a ``timeline`` argument, the :class:`~hiro.Timeline` will be
passed to it.

.. code-block:: python

    import hiro
    import time, datetime

    @hiro.Timeline(scale=50000)
    def sleeper():
        datetime.datetime.now()
        # OUT: '2013-11-30 14:27:43.409291'
        time.sleep(60*60) # effectively 72 ms
        datetime.datetime.now()
        # OUT: '2013-11-30 15:28:36.240675'

    @hiro.Timeline()
    def sleeper_aware(timeline):
        datetime.datetime.now()
        # OUT: '2013-11-30 14:27:43.409291'
        timeline.forward(60*60)
        datetime.datetime.now()
        # OUT: '2013-11-30 15:28:36.240675'


run_sync and run_async
======================

In order to execute certain callables within a :class:`~hiro.Timeline` context, two
shortcut functions are provided.

* :meth:`hiro.run_sync`
* :meth:`hiro.run_async`

Both functions return a :class:`~hiro.core.ScaledRunner` object which provides the following methods

* :meth:`~hiro.core.ScaledRunner.get_execution_time`: The actual execution time of the ``callable``
* :meth:`~hiro.core.ScaledRunner.get_response` (will either return the actual return value of ``callable`` or raise the exception that was thrown)

:meth:`~hiro.run_async` returns a derived class of :class:`hiro.core.ScaledRunner` that additionally provides the following methods

* :meth:`~hiro.core.ScaledAsyncRunner.is_running`: ``True/False`` depending on whether the callable has completed execution
* :meth:`~hiro.core.ScaledAsyncRunner.join`: blocks until the ``callable`` completes execution

.. code-block:: python


    import hiro
    import time

    def _slow_function(n):
        time.sleep(n)
        if n > 10:
            raise RuntimeError()
        return n

    runner = hiro.run_sync(10, _slow_function, 10)
    runner.get_response()
    # OUT: 10

    # due to the scale factor 10 it only took 1s to execute
    runner.get_execution_time()
    # OUT: 1.1052658557891846

    runner = hiro.run_async(10, _slow_function, 11)
    runner.is_running()
    # OUT: True
    runner.join()
    runner.get_execution_time()
    # OUT: 1.1052658557891846
    runner.get_response()
    # OUT: Traceback (most recent call last):
    # ....
    # OUT:   File "<input>", line 4, in _slow_function
    # OUT: RuntimeError




