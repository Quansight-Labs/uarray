.. currentmodule:: unumpy

Using ``unumpy``
================

``unumpy`` is an in-progress mirror of the NumPy API which allows the user
to dynamically switch out the backend that they are using. It also allows
auto-selection of the backend based on the arguments passed into a function.

Currently, only the following functions are supported:

* NumPy `universal functions <https://www.numpy.org/devdocs/reference/ufuncs.html>`_.

  * `ufunc reductions <https://www.numpy.org/devdocs/reference/generated/numpy.ufunc.reduce.html#numpy.ufunc.reduce>`_

* ufunc-based reductions

  * `sum <https://docs.scipy.org/doc/numpy/reference/generated/numpy.sum.html>`_
  * `prod <https://docs.scipy.org/doc/numpy/reference/generated/numpy.prod.html>`_
  * `min <https://docs.scipy.org/doc/numpy/reference/generated/numpy.amin.html>`_
  * `max <https://docs.scipy.org/doc/numpy/reference/generated/numpy.amax.html>`_
  * `any <https://docs.scipy.org/doc/numpy/reference/generated/numpy.any.html>`_
  * `all <https://docs.scipy.org/doc/numpy/reference/generated/numpy.all.html>`_

The following backends are supported:

* :obj:`numpy_backend.NumPyBackend`
* :obj:`torch_backend.TorchBackend`
* :obj:`xnd_backend.XndBackend`

You can use the :obj:`uarray.set_backend` decorator to set a backend and use the
desired backend. Note that not every backend supports every method.

Alternatively, the backend will be automatically used based on the type of the input
arrays passed in.
