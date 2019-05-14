``uarray``
==========

.. warning::
    :obj:`uarray` is a developer tool, it is not meant to be used directly by end-users.

.. warning::
    This document is meant to elicit discussion from the broader community and to help
    drive the direction that :obj:`uarray` goes towards. Examples provided here may not be
    immediately stable.

.. note::
    This page describes the overall philosophy behind :obj:`uarray`. For usage instructions,
    see the :obj:`uarray` API documentation page. If you are interested in an augmentation
    for NEP-22, please see the :obj:`unumpy` page.

:obj:`uarray` is a backend/dispatch mechanism with a focus on array computing and the
needs of the wider array community, by allowing a clean way to register an
implementation for any Python object (functions, classes, class methods, properties,
dtypes, ...), it also provides an important building block for
`NEP-22 <http://www.numpy.org/neps/nep-0022-ndarray-duck-typing-overview.html>`_.
It is meant to address the shortcomings of `NEP-18
<http://www.numpy.org/neps/nep-0018-array-function-protocol.html>`_ and `NEP-13
<https://www.numpy.org/neps/nep-0013-ufunc-overrides.html>`_;
while still holding nothing in :obj:`uarray` itself that's specific to array computing
or the NumPy API.

.. toctree::
    :hidden:
    :maxdepth: 3

    generated/uarray

    generated/unumpy




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
