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
  # OUT: '2013-11-30T10:45:09.583797'
  with hiro.Timeline() as timeline:

      # forward by an hour
      timeline.forward(60*60)
      datetime.now().isoformat()
      # OUT: '2013-11-30T11:45:09.585100'

      # jump forward by 10 minutes
      timeline.forward(timedelta(minutes=10))
      datetime.now().isoformat()
      # OUT: '2013-11-30T11:55:09.585115'

      # jump to yesterday and freeze forward/reverse
      timeline.freeze(datetime.now() - timedelta(days=-1))
      datetime.now().isoformat()
      # OUT: '2013-12-01T13:05:09'

      timeline.scale(5) # scale time by 5x
      time.sleep(5) # this will effectively only sleep for 1 second

      datetime.now().isoformat()
      # OUT: '2013-12-01T13:05:09'

      timeline.reverse(timedelta(year=1))

      print datetime.now().isoformat()
      # OUT: '2013-12-01T13:05:09'


Scaled Timeline Context
=======================
The ``ScaledTimeline`` context behaves identically to the ``Timeline`` context
with the one exception that it can be initialized with a default scale ``factor``

.. code-block:: python

      import hiro
      from datetime import timedelta, datetime, date
      import time

      # all time operations will occur at 50000x
      with hiro.ScaledTimeline(factor=50000):
          datetime.now().isoformat()
          # OUT: '2013-11-30T12:37:56.051953'

          # sleep for an hour
          time.sleep(60*60) # effectively 72 ms

          datetime.now().isoformat()
          # OUT: '2013-11-30T13:38:32.447884'

          # sleep for a day
          time.sleep(60*60*24) # effectively 1.7 seconds

          date.today().isoformat()
          # OUT: '2013-12-01'


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


