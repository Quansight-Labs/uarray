.. currentmodule:: uarray

.. _getting_started:

Getting started with ``uarray``
===============================

The core building blocks of :obj:`uarray` are :obj:`MultiMethod` objects and
:obj:`Backend` objects. The former defines a (possibly abstract, but definitely
overridable) method. The latter defines implementations for that method (or overrides,
in the case when there is a default implementation).

:obj:`Backend` s can be preferred by using the :obj:`set_backend` context manager,
which will remember the order of the preferred backends in a thread-safe way.

Another related context manager is the :obj:`skip_backend` context manager. It skips a
backend completely. Its intended use is for libraries that define ``uarray`` methods
that use the same method internally, to avoid infinite recursion.

:obj:`Backend` s can also be permanently registered using the :obj:`register_backend`
function. Remember that registered backends will be called in an indeterminate order.

:obj:`Backend` s can register an implementation of a method using the
:obj:`Backend.register_implementation` method.

The :obj:`create_multimethod` decorator provides an easy way to define a method, and
the :obj:`register_implementation` decorator does the same for registering an
implementation.
