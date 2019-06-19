.. currentmodule:: uarray

.. _mmauthordocs:

Documentation for API authors
=============================

.. testsetup:: mmtutorial
    import uarray as ua

Multimethods are the most important part of :obj:`uarray`. They
are created via the :obj:`generate_multimethod` function. Multimethods
define the API of a project, and backends have to be written against
this API. You should see :ref:`libauthordocs` for how to define a
backend against the multimethods you write, or :ref:`userdocs` for
how to switch backends for a given API.

A multimethod has the following parts:

* Domain
* Argument extractor
* Argument replacer
* Default implementation

We will go through each of these in detail now.

Domain
------

See the :ref:`glossary for domain <DomainGlossary>`.

Argument extractor
------------------

An argument extractor extracts arguments :ref:`marked <MarkingGlossary>` as a
given type from the list of given arguments. Note that the objects extracted
don't necessarily have to be in the list of arguments, they can be arbitrarily
nested within the arguments. For example, extracting each argument from a list
is a possibility. Note that the order is important, as it will come into play
later. This function should return an iterable of :obj:`Dispatchable`.

This function has the same signature as the multimethod itself, and
the documentation, name and so on are copied from the argument extractor
via :obj:`functools.wraps`.

Argument replacer
-----------------

The argument replacer takes in the arguments and dispatchable arguments, and its
job is to replace the arguments previously extracted by the argument extractor
by other arguments provided in the list. The signature of this function is
``(kwargs, dispatchable_args)``, and it returns the updated ``kwargs``. Here
``kwargs`` includes also the positional arguments from the function call, now
stored as if they were called as keyword arguments. If the function contains any
varargs (e.g. ``def f(*args)``) then it is given in ``kwargs`` as a single
parameter. We realise this is a hard problem in general, so we have provided a
few simplifications, such as that the default-valued keyword arguments will be
removed from the list.

We recommend following the pattern in `this file <https://github.com/Quansight-Labs/uarray/blob/master/unumpy/multimethods.py>`_
for optimal operation: passing the ``kwargs`` into a function with a
similar signature and then return the modified ``kwargs``.

Default implementation
----------------------

This is a default implementation for the multimethod. This should have the same
signature as the original multimethod, except that there can be no position-only
parameters and any varargs should be rewritten as normal arguments taking a
tuple. It can also be used to provide one multimethod in terms of others, even
if the default implementation for the downstream multimethods is not defined.

Examples
--------

Examples of writing multimethods are found in `this file <https://github.com/Quansight-Labs/uarray/blob/master/unumpy/multimethods.py>`_.
It also teaches some advanced techniques, such as overriding instance methods,
including ``__call__``. The same philosophy may be used to override properties,
static methods and class methods.
