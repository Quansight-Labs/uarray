.. currentmodule:: uarray

.. _userdocs:

End-user quickstart
===================

Ideally, the only thing an end-user should have to do is set the backend and
and its options. Given a backend, you (as the end-user) can decide to
do one of two things:

* Set the backend permanently (use the :obj:`set_global_backend` function).
* Set the backend temporarily (use the :obj:`set_backend` context manager).

Also of note may be the :obj:`BackendNotImplementedError`, which is raised
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
method. For this, you have to provide an additional piece of information,
which is the domain. The domain, by convention, is the module where the
multimethods reside, or one of its parents.

.. code:: python3

    import uarray as ua

    ua.set_global_backend('mydomain', mybackend)

    # Use relevant multimethods here.
