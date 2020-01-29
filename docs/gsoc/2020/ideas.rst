GSoC 2020 project ideas
=======================

Introduction
------------

This is the Google Summer of Code 2020 (GSoC'20) ideas page for ``uarray``,
``unumpy`` and ``udiff``. The ``uarray`` library is is a backend mechanism
geared towards array computing, but intended for general use. ``unumpy`` is an
incomplete stub of the NumPy API that can be dispatched by ``uarray``.
``udiff`` is a general-purpose automatic differentiation library built
on top of ``unumpy`` and ``uarray``.

This page lists a number of ideas for Google Summer of Code projects for
``uarray``, plus gives some pointers for potential GSoC students on how to get
started with contributing and putting together their application.

Guidelines & requirements
-------------------------

``uarray`` plans to participate in GSoC'20 under the `umbrella of Python Software Foundation <http://python-gsoc.org/>`_.

We expect from students that they're at least comfortable with Python
(intermediate level). Some projects may also require C++ or C skills.
Knowing how to use Git is also important; this can be learned before the
official start of GSoC if needed though.

If you have an idea of what you would like to work on (see below for ideas)
and are considering participating:


1. Read the `PSF page <http://python-gsoc.org/>`_ carefully, it contains
   important advice on the process.
2. Read `advice on writing a proposal <http://turnbull.sk.tsukuba.ac.jp/Blog/SPAM.txt#how-to-spam-in-detail>`_
   (written with the Mailman project in mind, but generally applicable)
3. Make a enhancement/bugfix/documentation fix -- it does not have to be big,
   and it does not need to be related to your proposal. Doing so before
   applying for the GSoC is a hard requirement for ``uarray``. It helps
   everyone you get some idea how things would work during GSoC.
4. Start writing your proposal early, post a draft to the issue tracker and
   iterate based on the feedback you receive. This will both improve the
   quality of your proposal and help you find a suitable mentor.

Contact
-------

If you have a question *after checking all guideline pages above*, you can
open an issue in the issue tracker, but feel free to
`chat with us on Gitter <https://gitter.im/Plures/uarray>`_ if you need
clarification regarding any of the projects. Keep in mind that you might not
get a response right away, but we will endeavour to respond as early as possible.


``uarray`` project ideas
------------------------

``uarray``: Add querying for state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding querying for the `uarray._BackendState <https://github.com/Quansight-Labs/uarray/blob/39c49b6efe6817b46af9c6702e6aa0264b89bcf5/uarray/_uarray_dispatch.cxx#L188>`_
object will allow users of ``uarray`` to see what's inside the opaque object.
Some parts can be re-used from the `pickling machinery <https://github.com/Quansight-Labs/uarray/blob/39c49b6efe6817b46af9c6702e6aa0264b89bcf5/uarray/_uarray_dispatch.cxx#L210>`_.

It can also help downstream users to access the parameters of the currently
set backend, which is a planned feature of ``uarray``. Here is a list of goals
for this project:

* Allow downstream projects to query the list of backends.
* Allow downstream projects to query the list of parameters for a backend.

This would enable, for example, the following use-cases:

* Allow a downstream library to detect a backend and run specialised code for
  it.
* Allow a downstream library to fail-fast on a known-unsupported backend.

This project has a straightforward design and needs some implementation work,
and will require interacting with the mentors to implement and polish. The accepted
student will get an outline of the desired API, along with some failing tests and
doctests. The student will make a pull request to implement the desired functionality
so that the tests pass.

* Required knowledge: Python C-API and C++
* Difficulty level: medium
* Potential mentors: Peter Bell and Hameer Abbasi

``uarray``: Allow subdomains
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This idea would allow a backend to encompass functions from more than one
domain.

The primary goal of this project would be:

* Develop a system that allows, via some kind of matching mechanism, to select
  which domains it supports, **while maintaining backward compatibility**.

This would allow a backend targeting NumPy to also target, for example, the
``numpy.random`` submodule. Since the domain for functions in
``numpy.random`` will be just that: ``numpy.random``, it won't match
backends defined with the ``numpy`` domain, since it's an exact string
match.

The second objective here would be to allow backends to target submodules
of projects rather than the whole project. For example, targeting just
``numpy.random`` or ``numpy.fft`` without targeting all of NumPy.

For more detail see `this issue <https://github.com/Quansight-Labs/uarray/issues/189>`_.

This project has a somewhat complicated design and needs some involved
implementation work, and will require interacting with the mentors to flesh
out and work through.

* Required knowledge: Python C-API and C++
* Difficulty level: hard
* Potential mentors: Peter Bell and Hameer Abbasi

``unumpy``: Expand overall coverage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project is split into two parts:

* Adding further coverage of the NumPy API.
* Adding more backends to ``unumpy``.

We realise this is a large (possibly open-ended) undertaking, and so there
will need to be a minimum amount of work done in order to pass (~150 function stubs,
if time allows a `JAX <https://jax.readthedocs.io/en/latest/>`_ backend). You may
see the existing methods and figure out how they are written using a combination
of the `documentation for writing multimethods <https://uarray.readthedocs.io/en/latest/multimethod_docs.html>`_
and the `already existing multimethods in this file <https://github.com/Quansight-Labs/unumpy/blob/30c4afde16fbbb231cbc1e20d28cf5f0a8527285/unumpy/_multimethods.py>`_.
For writing backends, you can see the `documentation for backends <https://uarray.readthedocs.io/en/latest/libauthor_docs.html>`_
in combination with the already existing backends in `this directory <https://github.com/Quansight-Labs/unumpy/tree/30c4afde16fbbb231cbc1e20d28cf5f0a8527285/unumpy>`_.

* Required knowledge: Python (intermediate level)
* Difficulty level: easy
* Potential mentors: Prasun Anand and Hameer Abbasi

``udiff``: Completion and Packaging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This requires completion and packaging of the `udiff <https://github.com/Quansight-Labs/udiff>`_ library. Potential
goals include:

1. Publishing an initial version to PyPI. Here's a `guide <https://realpython.com/pypi-publish-python-package/>`_
   on how to do that.
2. Adding matrix/tensor calculus support.

   * For this, you can see the `matrix cookbook <https://www.math.uwaterloo.ca/~hwolkowi/matrixcookbook.pdf>`_.
     Don't be intimidated! There will only be five or so equations you have to
     pull out of the matrix cookbook and implement, most prominently, the
     equation for matrix multiplication.
   * `Here <https://github.com/Quansight-Labs/udiff/blob/40975788639c2c93ebfb96c44a07d8ab01fbcbad/udiff/_builtin_diffs.py>`_
     is how derivatives are registered.
   * The second task here will be to add the "separation" between the data
     dimensions and the differentiation dimensions. For example, the input
     could be a vector, or an array of scalars, and this might need to be
     taken into account when doing the differentiation. That will require
     some work in `this file <https://github.com/Quansight-Labs/udiff/blob/40975788639c2c93ebfb96c44a07d8ab01fbcbad/udiff/_diff_array.py>`_,
     and possibly `this one as well <https://github.com/Quansight-Labs/udiff/blob/40975788639c2c93ebfb96c44a07d8ab01fbcbad/udiff/_diff_array.py>`_.

3. Adding tests.

  * This will require calculating a few derivatives by hand and making sure
    they match up with what ``udiff`` computes.
  * We will use the `PyTest framework <https://docs.pytest.org/en/latest/>`_.

4. Adding documentation on use, which will be fairly minimal. We will learn to
   set up `Sphinx <http://www.sphinx-doc.org/en/master/>`_, and add some documentation.
5. Publishing a final version to PyPI.

This project has a somewhat some minimal design and needs some involved
implementation work. It will allow the accepted student to get an idea of
what it's like to actually publish, test and document a small Python package.

* Required knowledge: Python (intermediate level) and calculus
* Difficulty level: medium
* Potential mentors: Prasun Anand and Hameer Abbasi
