.. currentmodule:: uarray

.. _userdocs:

End-user quickstart
===================

Ideally, the only thing an end-user should have to do is set the backend
and its options. Given a backend, you (as the end-user) can decide to
do one of two things:

* Set the backend permanently (use the :obj:`set_global_backend` function).
* Set the backend temporarily (use the :obj:`set_backend` context manager).

.. note::
    API authors may want to wrap these methods and provide their own methods.

Also of a note may be the :obj:`BackendNotImplementedError`, which is raised
when none of the selected backends have an implementation for a multimethod.

Setting the backend temporarily
-------------------------------

To set the backend temporarily, use the :obj:`set_backend` context manager.

.. code:: python3

    import uarray as ua

    with ua.set_backend(mybackend):
        # Use multimethods (or code dependent on them) here.

Setting the backend permanently
-------------------------------

To set the backend permanently, use the :obj:`set_global_backend`
method. It is a recommendation that the global backend should not
depend on any other backend, as it is not guaranteed that another
backend will be available.

You can also register backends other than the global backend for permanent
use, but the global backend will be tried first outside of a :obj:`set_backend`
context. This can be done via :obj:`register_backend`.


.. code:: python3

    import uarray as ua

    ua.set_global_backend(mybackend)

    # Use relevant multimethods here.
