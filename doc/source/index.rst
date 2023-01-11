
########################################################
Hiro - time manipulation utilities for testing in python
########################################################

Often testing code that can be time dependent can become either fragile or
slow. Hiro provides context managers and utilities to either freeze, accelerate
or decelerate and jump between different points in time. Functions exposed by the
standard library's ``time``, ``datetime`` and ``date`` modules are patched within
the contexts exposed.


.. include:: intro.rst

.. toctree::
    :maxdepth: 4
    :hidden:

    intro
    api
    project
    changelog
