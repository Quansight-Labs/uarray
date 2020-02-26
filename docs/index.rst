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
    see the :obj:`uarray` API documentation page. If you are interested in augmentation
    for NEP-22, please see the :obj:`unumpy` page.

`uarray` is a backend system for Python that allows you to separately define an API,
along with backends that contain separate implementations of that API.

`unumpy` builds on top of `uarray`. It is an effort to specify the core NumPy API, and
provide backends for the API.

What's new in ``uarray``?
-------------------------

:obj:`uarray` is, to our knowledge, the first backend-system for Python that's generic
enough to cater to the use-cases of many libraries, while at the same time, being
library independent.

:obj:`unumpy` is the first approach to leverage :obj:`uarray` in order to build a
generic backend system for (what we hope will be) the core NumPy API. It will be
possible to create a backend object and use that to perform operations. In addition,
it will be possible to change the used backend via a context manager.

Benefits for end-users
----------------------

End-users can easily take their code written for one backend and use it on another
backend with a simple switch (using a Python context manager). This can have any number
of effects, depending on the functionality of the library. For example:

* For Matplotlib, changing styles of plots or producing different windows or image
  formats.
* For Tensorly, providing a different computation backend that can be distributed or
  target the GPU or sparse arrays.
* For :obj:`unumpy`, it can do a similar thing: provide users with code they already
  wrote for `numpy` and easily switch to a different backend.

Benefits for library authors
----------------------------

To library authors, the benefits come in two forms: First, it allows them to build their
libraries to be implementation independent. In code that builds itself on top of
:obj:`unumpy`, it would be very easy to target the GPU, use sparse arrays or do any kind
of distributed computing.

The second is to allow a way to separate the interface from implementation, and easily
allow a way to switch an implementation.

Relation to the NumPy duck-array ecosystem
------------------------------------------

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

Where to from here?
-------------------

Choose the documentation page relevant to you:

* :ref:`mmauthordocs`
* :ref:`libauthordocs`
* :ref:`userdocs`

.. toctree::
    :hidden:
    :maxdepth: 3

    enduser_docs

    libauthor_docs

    multimethod_docs

    glossary

    generated/uarray

    gsoc/2020/ideas


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
