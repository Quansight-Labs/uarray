Welcome to uarray's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

This document specifies the uarray interface. The uarray interface defines a
set of APIs that compliant back-ends will have to introduce in order to support
the uarray interface.

Desired usage
-------------

This section defines the desired usage of objects implementing the uarray
protocol.

.. code:: python

    import numpy as np
    import uarray as ua
    with ua.backend(np):
        # instantiates a NumPy array
        x = ua.ones((5, 5), dtype='int64')
        # do computation on NumPy
        y = x + x
        z = x ** 2

    import xnd
    with ua.backend(xnd):
        # instantiates an xnd array
        x = ua.ones((5, 5), dtype='int64')
        # do computation on xnd array
        y = x + x
        z = x ** 2

Example implementation
----------------------

Here is an example implementation of a back-end:

.. code:: python

    import numpy as np
    from uarray.backend import implements, register_type

    register_type(np, np.ndarray)

    # Can also be pointer to LLVM code for speed
    @implements(np)
    def __ua_construct__(shape, dtype):
        return np.empty(shape, dtype=dtype)

    @implements(np)
    def __ua_shape__(x):
        return x.shape

    @implements(np)
    def __ua_getitem__(x, idx):
        return x[idx]

    @implements(np)
    def __ua_setitem__(x, idx, value):
        x[idx] = value

    @implements(np)
    def __ua_mtype__(x):
        return str(x.dtype)

    # Optional for speed
    @implements(np)
    def __ua_gufunc__(func_name, func_sig, arr_args, opts):
        if func_name == 'ones':
            return np.ones(opts['shape'], opts['dtype'])
        if func_name == 'add':
            return arr_args[0] + arr_args[1]
        if func_name == 'power':
            return arr_args[0] ** arr_args[1]

When this code is run, the NumPy back-end will be registered and work with
uarray. The benefit of this approach is that no changes are needed in NumPy
itself.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
