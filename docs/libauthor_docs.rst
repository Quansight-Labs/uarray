.. currentmodule:: uarray

.. _libauthordocs:

Documentation for backend providers
===================================

Backend providers can provide a back-end for a defined API within
the :obj:`uarray` ecosystem. To find out how to define your own
API with :obj:`uarray`, see :ref:`mmauthordocs`. To find out how
your backend will be provided, use :ref:`userdocs`.

Backend providers need to be aware of three protocols: ``__ua_domain__``,
``__ua_function__`` and ``__ua_convert__``. The first two are mandatory and
the last is optional.

``__ua_domain__``
-----------------

``__ua_domain__`` is a string containing the domain of the backend. This is,
by convention, the name of the module (or one of its dependencies or parents)
that contains the multimethods. For example, ``scipy`` and ``numpy.fft`` could
both be in the ``numpy`` domain or one of its subdomains.

Additionally, ``__ua_domain__`` can be a sequence of domains, such as a tuple or
list of strings. This allows a single backend to implement functions from more
than one domain.

``__ua_function__``
-------------------

This is the most important protocol, one that defines the implementation of a
multimethod. It has the signature ``(method, args, kwargs)``.
Note that it is called in this form, so if your backend is an object instead of
a module, you should add ``self``. ``method`` is the multimethod being called,
and it is guaranteed that it is in the same domain as the backend. ``args`` and
``kwargs`` are the arguments to the function, possibly after conversion
(explained below)

Returning :obj:`NotImplemented` signals that the backend does not support this
operation.

``__ua_convert__``
------------------

All dispatchable arguments are passed through ``__ua_convert__`` before being
passed into ``__ua_function__``. This protocol has the signature
``(dispatchables, coerce)``, where ``dispatchables`` is iterable of
:obj:`Dispatchable` and ``coerce`` is whether or not to coerce forcefully.
``dispatch_type`` is the mark of the object to be converted, and ``coerce``
specifies whether or not to "force" the conversion. By convention, operations
larger than ``O(log n)`` (where ``n`` is the size of the object in memory)
should only be done if ``coerce`` is ``True``. In addition, there are arguments
wrapped as non-coercible via the ``coercible`` attribute, if these *must* be
coerced, then one should return ``NotImplemented``.

A convenience wrapper for converting a single object,
:obj:`wrap_single_convertor` is provided.

Returning :obj:`NotImplemented` signals that the backend does not support the
conversion of the given object.

:obj:`skip_backend`
-------------------

If a backend consumes multimethods from a domain and provides multimethods
for that same domain, it may wish to have the ability to use multimethods while
excluding itself from the list of tried backends in order to avoid infinite
recursion. This allows the backend to implement its functions in terms of
functions provided by other backends. This is the purpose of the
:obj:`skip_backend` decorator.

The process that takes place when the backend is tried
------------------------------------------------------

First of all, the backend's ``__ua_convert__`` method is tried. If this returns
:obj:`NotImplemented`, then the backend is skipped, otherwise, its
``__ua_function__`` protocol is tried. If a value other than
:obj:`NotImplemented` is returned, it is assumed to be the final
return value. Any exceptions raised are propagated up the call stack, except a
:obj:`BackendNotImplementedError`, which signals a skip of the backend. If all
backends are exhausted, or if a backend with its ``only`` flag set to ``True``
is encountered, a :obj:`BackendNotImplementedError` is raised.

Examples
--------

Examples for library authors can be found `in the source of unumpy.numpy_backend <https://github.com/Quansight-Labs/unumpy/blob/master/unumpy/numpy_backend.py>`_
and other ``*_backend.py`` files in `this directory <https://github.com/Quansight-Labs/unumpy/tree/master/unumpy>`_.
