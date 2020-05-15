uarray
======

.. automodule:: uarray



   .. rubric:: Functions

   .. autosummary::
      :toctree:

      all_of_type
      create_multimethod
      generate_multimethod
      mark_as
      set_backend
      set_global_backend
      register_backend
      clear_backends
      skip_backend
      wrap_single_convertor
      get_state
      set_state
      reset_state
      determine_backend
      determine_backend_multi





   .. rubric:: Classes

   .. autosummary::
      :toctree:

      Dispatchable





   .. rubric:: Exceptions

   .. autosummary::
      :toctree:

      BackendNotImplementedError


Design Philosophies
-------------------

The following section discusses the design philosophies of :obj:`uarray`, and the
reasoning behind some of these philosophies.

Modularity
^^^^^^^^^^

:obj:`uarray` (and its sister modules :obj:`unumpy` and others to come) were designed
from the ground-up to be modular. This is part of why :obj:`uarray` itself holds
the core backend and dispatch machinery, and :obj:`unumpy` holds the actual
multimethods. Also, :obj:`unumpy` can be developed completely separately to
:obj:`uarray`, although the ideal place to have it would be NumPy itself.

However, the benefit of having it separate is that it could span multiple
NumPy versions, even before NEP-18 (or even NEP-13) was available. Another
benefit is that it can have a faster release cycle to help it achieve this.

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
backends are *only* passed types they know how to dispatch over when
deciding whether or not to use that backend. For example, if a backend
doesn't know how to dispatch over dtypes, it won't be asked to decide
based on that front.

Methods can have a default implementation in terms of other methods,
but they're still overridable.

This means that only one framework is needed to, for example, dispatch
over ``ufunc`` s, arrays, dtypes and all other primitive objects in NumPy,
while keeping the core :obj:`uarray` code independent of NumPy and even
:obj:`unumpy`.

Backends can span modules, so SciPy could jump in and define its own methods
on NumPy objects and make them overridable within the NumPy backend.

User Choice
^^^^^^^^^^^

The users of :obj:`unumpy` or :obj:`uarray` can choose which backend they want
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

    with ua.use_backend(DaskBackend):
        # Write all your code here
        # It will prefer the Dask backend

There is no default backend, to :obj:`unumpy`, NumPy is just another backend. One
can register backends, which will all be tried in indeterminate order when no
backend is selected.

Addressing past flaws
^^^^^^^^^^^^^^^^^^^^^

The progress on NumPy's side for defining an override mechanism has been slow, with
NEP-13 being first introduced in 2013, and with the wealth of dispatchable objects
(including arrays, ufuns, and dtypes), and with the advent of libraries like Dask,
CuPy, Xarray, PyData/Sparse, and XND, it has become clear that the need for alternative
array-like implementations is growing. There are even other libraries like PyTorch, and
TensorFlow that'd be possible to express in NumPy API-like terms. Another example
includes the Keras API, for which an overridable ``ukeras`` could be created, similar
to :obj:`unumpy`.

:obj:`uarray` is intended to have fast development to fill the need posed by these
communities, while keeping itself as general as possible, and quickly reach maturity,
after which backward compatibility will be guaranteed.

Performance considerations will come only after such a state has been reached.
