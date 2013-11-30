*********************************************
Hiro - time manipulation utilities for python
*********************************************

.. image:: https://travis-ci.org/alisaifee/hiro.png?branch=master
    :target: https://travis-ci.org/alisaifee/hiro
.. image:: https://coveralls.io/repos/alisaifee/hiro/badge.png?branch=master
    :target: https://coveralls.io/r/alisaifee/hiro?branch=master

=====================
Hiro context managers
=====================


Timeline context
================
The ``hiro.Timeline`` context manager hijacks a few commonly used time functions
to allow time manipulation within its context. Specifically ``time.sleep``, ``time.time``,
``time.gmtime``, ``datetime.now``, ``datetime.utcnow`` and ``datetime.today`` behave according the configuration of the context.

The context provides the following manipulation options:

* ``rewind``: accepts seconds as an integer or a ``timedelta`` object.
* ``forward``: accepts seconds as an integer or a ``timedelta`` object.
* ``freeze``: accepts a floating point time since epoch or ``datetime`` or ``date`` object to freeze the time at.
* ``unfreeze``: resumes time from the point it was frozen at.
* ``scale``: accepts a floating point to accelerate/decelerate time by. ``> 1 = acceleration,  < 1 = deceleration``
* ``reset``: resets all time alterations.

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

Scaled Timeline Context
=======================
The ``ScaledTimeline`` context behaves identically to the ``Timeline`` context
with the one exception that it can be initialized with a default scale ``factor``

.. code-block:: python

      import hiro
      from datetime import timedelta, datetime, date
      import time

      # all time operations will occur at 10000x
      with hiro.ScaledTimeline(factor=10000) as timeline:
          datetime.now().isoformat()
          # OUT: '2013-12-01T06:49:33.777745'

          # sleep for an hour
          time.sleep(60*60) # effectively 360 ms

          datetime.now().isoformat()
          # OUT: '2013-12-01T07:49:47.097142'

          # accelerate further
          timeline.scale(50000)

          # sleep for a day
          time.sleep(60*60*24) # effectively 1.7 seconds

          datetime.now().isoformat()
          # OUT: '2013-12-02T06:50:06.726242'
          datetime.utcnow().isoformat()
          # OUT: '2013-12-01T22:50:13'
          date.today().isoformat()
          # OUT: '2013-12-02'



``ScaledTimeline`` can additionally be used as a decorator

.. code-block:: python

    import hiro
    import time, datetime

    @hiro.ScaledTimeline(50000)
    def sleeper():
        datetime.datetime.now()
        # OUT: '2013-11-30 14:27:43.409291'
        time.sleep(60*60) # effectively 72 ms
        datetime.datetime.now()
        # OUT: '2013-11-30 15:28:36.240675'


==============
Hiro executors
==============

In order to execute certain callables within a ``ScaledTimeline`` context, two
shortcut functions are provided.

* ``run_sync(factor=1, callable, *args, **kwargs)``
* ``run_async(factor=1, callable, *args, **kwargs)``

Both functions return a ``ScaledRunner`` object which provides the following methods

* ``get_execution_time``: The actual execution time of the ``callable``
* ``get_response`` (will either return the actual return value of ``callable`` or raise the exception that was thrown)

``run_async`` returns a derived class of ``ScaledRunner`` that additionally provides the following methods

* ``is_running``: ``True/False`` depending on whether the callable has completed execution
* ``join``: blocks until the ``callable`` completes execution


Example
=======

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



.. figure:: http://d2tq98mqfjyz2l.cloudfront.net/image_cache/1335749604395082.jpg
   :alt: Hiro Nakamura
   :align: center


   Yatta!

   -- Hiro Nakamura


