.. uarray documentation master file, created by
   sphinx-quickstart on Tue Mar 12 19:05:25 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ``uarray``'s documentation
=====================================

.. warning::
    ``uarray`` is a developer tool, it is not meant to be used directly by end-users.

.. warning::
    This document is meant to elicit discussion from the broader community and to help
    drive the direction that ``uarray`` goes towards. Examples proviced here may not be
    immediately stable.

``uarray`` is a backend/dispatch mechanism with a focus on array computing and the
needs of the wider array community. It is meant to address the shortcomings of `NEP-18
<http://www.numpy.org/neps/nep-0018-array-function-protocol.html>`_ and `NEP-13
<https://www.numpy.org/neps/nep-0013-ufunc-overrides.html>`_; while also being a
comprehensive solution to `NEP-22 <http://www.numpy.org/neps/nep-0022-ndarray-duck-typing-overview.html>`_,
while still holding nothing in ``uarray`` itself that's specific to array computing
or the NumPy API.

Design Philosophies
-------------------

The following section discusses the design philosophies of ``uarray``, and the
reasoning behind some of these philosophies.

Modularity
^^^^^^^^^^

``uarray`` (and its sister modules ``unumpy`` and others to come) were designed
from the ground-up to be modular. This is part of why ``uarray`` itself holds
the core backend and dispatch machinery, and ``unumpy`` holds the actual
multimethods. Also, ``unumpy`` can be developed completely separately to
``uarray``, although the ideal place to have it would be NumPy itself.

However, the benefit to having it separate is that it could span multiple
NumPy versions, even before NEP-18 (or even NEP-13) was available.

Separate Imports
^^^^^^^^^^^^^^^^

Code wishing to use the backend machinery for NumPy (as an example) will
use the statement ``import unumpy as np`` instead of the usual
``import numpy as np``. This is deliberate: it makes dispatching opt-in
instead of being forced to use it, and the overhead associated with it.
However, a package is free to define its main methods as the dispatchable
versions, thereby allowing dispatch on the default implementation.

Extensibility *and* Choice
^^^^^^^^^^^^^^^^^^^^^^^^^^

If some effort is put into the dispatch machinery, it's possible to
dispatch over arbitrary objects --- including arrays, dtypes, and
so on. A method defines the type of each dispatchable argument, and
backends are *only* passed types they know how to dispatch over.

Methods can have a default implementation in terms of other methods,
but they're still overridable.

This means that only one framework is needed to, for example, dispatch
over ``ufunc`` s, arrays, dtypes and all other primitive objects in NumPy,
while keeping the core ``uarray`` code independent of NumPy and even ``unumpy``.

Backends can span modules, so SciPy could jump in and define its own methods
on NumPy objects and make them overridable within the NumPy backend.

User Choice
^^^^^^^^^^^

The users of ``unumpy`` or ``uarray`` can choose which backend they want
to prefer with a simple context manager. They also have the ability to
force a backend, and to skip a backend. This is useful for array-like
objects that provide other array-like objects by composing them. For
example, Dask could perform all its blockwise function calls with the
following psuedocode (obviously, this is simplified):

.. code:: python

    in_arrays = extract_inner_arrays(input_arrays)
    out_arrays = []
    for input_arrays_single in in_arrays:
        args, kwargs = blockwise_function.replace_args_kwargs(
            args, kwargs, input_arrays_single)
        with ua.skip_backend(DaskBackend):
            out_arrays_single = blockwise_function(*args, **kwargs)
        out_arrays.append(out_arrays_single)

    return combine_arrays(out_arrays)

A user would simply do the following:

.. code:: python

    x = da.array([a, b, c])

    # Anything that uses x will (usually) use the Dask backend

    with ua.use_backend(DaskBackend):
        # Write all your code here
        # It will prefer the Dask backend

Addressing past flaws
^^^^^^^^^^^^^^^^^^^^^

The progress on NumPy's side for defining an override mechanism has been slow, with
NEP-13 being first introduced in 2013, and with the wealth of dispatchable objects
(including arrays, ufuns and dtypes), and with the advent of libraries like Dask,
CuPy, XArray, PyData/Sparse and Xnd, it has become clear that the need for alternative
array-like implementations is growing. There are even other libraries like PyTorch, and
TensorFlow that'd be possible to express in NumPy API-like terms. Another example includes
the Keras API.

``uarray`` is intended to have fast development to fill the need posed by these
communities, while keeping itself as general as possible, and quickly reach maturity,
after which backwards compatibility will be guaranteed.

Performance considerations will come only after such a state has been reached.

Object-Orientation
^^^^^^^^^^^^^^^^^^

``uarray`` and its submodules are written in an object-oriented fashion first, but a
functional interface is provided for ease of use, including decorators. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
