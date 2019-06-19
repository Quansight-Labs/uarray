.. currentmodule:: uarray

.. _libauthordocs:

Documentation for backend providers
===================================

Backend providers can provide a back-end for a defined API within
the :obj:`uarray` ecosystem. To find out how to define your own
API with :obj:`uarray`, see :ref:`mmauthordocs`. To find out how
your backend will be provided, use :ref:`userdocs`.

Backend providers need to be aware of three protocols: ``__ua_domain__``,
``__ua_function__`` and ``__ua_convert__``, all of which are mandatory on
all backends.

``__ua_domain__``
-----------------

``__ua_domain__`` is a string containing the domain of the backend. This is,
by convention, the name of the module (or one of its dependencies or parents)
that contain the multimethods. For example, ``scipy`` and ``numpy.fft`` could
both use the ``numpy`` domain.

``__ua_function__``
-------------------

This is the most important protocol, one that defines the implementation of a
multimethod. It has the signature ``(method, kwargs)``. Note that it is called
in this form, so if your backend is an object instead of a module, you should
add ``self``. ``method`` is the multimethod being called, and it is guaranteed
that it is in the same domain as the backend. ``kwargs`` is a ``dict``
containing all arguments to the function, possibly after conversion (explained
below). If the function contains any varargs (e.g. ``def f(*args)``) then it is
given in ``kwargs`` as a single parameter.

Returning :obj:`NotImplemented` signals that the backend does not support this
operation.

``__ua_convert__``
------------------

All dispatchable arguments are passed through ``__ua_convert__`` before being
passed into ``__ua_function__``. This protocol has the signature
``(value, dispatch_type, coerce)``. ``value`` is the value to convert,
``dispatch_type`` is the mark of the object to be converted, and ``coerce``
specifies whether or not to "force" the conversion. By convention, operations
larger than ``O(log n)`` (where ``n`` is the size of the object in memory)
should only be done if ``coerce`` is ``True``.

Returning :obj:`NotImplemented` signals that the backend does not support
conversion of the given object.

:obj:`skip_backend`
-------------------

If a backend consumes multimethods from a domain, and provides multimethods
for that same domain, it may wish to have the ability to use multimethods while
excluding itself from the list of tried backends in order to avoid infinite
recursion. This allows the backend to implement its functions in terms of
functions provided by other backends. This is the purpose of the
:obj:`skip_backend` decorator.

Examples
--------

Examples for library authors can be found `in the source of unumpy.numpy_backend <https://github.com/Quansight-Labs/uarray/blob/master/unumpy/numpy_backend.py>`_
and other ``*_backend.py`` files in `this directory <https://github.com/Quansight-Labs/uarray/tree/master/unumpy>`_.
