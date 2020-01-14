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
3. Look at the guidelines on how to contribute to Scipy.
4. Make a enhancement/bugfix/documentation fix -- it does not have to be big,
   and it does not need to be related to your proposal. Doing so before
   applying for the GSoC is a hard requirement for ``uarray``. It helps
   everyone you get some idea how things would work during GSoC.
5. Start writing your proposal early, post a draft to the the mentors' email
   addresses mailing list and iterate based on the feedback you receive. This
   will both improve the quality of your proposal and help you find a suitable mentor.

Contact
-------

If you have a question *after checking all guideline pages above*, you can
email the mentors.

``uarray`` project ideas
------------------------

``uarray``: Add querying for state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding querying for the ``uarray._BackendState`` object will allow users of
``uarray`` to see what's inside the opaque object. Some parts can be re-used
from the pickling machinery.

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
and will require interacting with the mentors to implement and polish.

* Required knowledge: Python C-API and C++
* Difficulty level: easy
* Potential mentors: Peter Bell and Hameer Abbasi

``uarray``: Allow subdomains
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This idea would allow a backend to encompass functions from more than one domain.

The primary goal of this project would be:

* Develop a system that allows, via some kind of matching mechanism, to select
  which domains it supports, **while maintaining backward compatibility**.

This would allow a backend targeting NumPy to also target, for example, the
``numpy.random`` submodule.

This project has a somewhat complicated design and needs some involved
implementation work, and will require interacting with the mentors to flesh
out and work through.

* Required knowledge: Python C-API and C++
* Difficulty level: easy
* Potential mentors: Peter Bell and Hameer Abbasi

``unumpy``: Expand overall coverage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project is split into two parts:

* Adding further converage of the NumPy API.
* Adding more backends to NumPy.

We realise this is a large (possibly open-ended) undertaking, and so there
will need to be a minimum amount of work done in order to pass.

* Required knowledge: Python (intermediate level)
* Difficulty level: easy
* Potential mentors: Prasun Anand and Hameer Abbasi

``udiff``: Completion and Packaging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This requires completion and packaging of the ``udiff`` library. Potential
goals include:

1. Publishing an initial version to PyPI.
2. Adding matrix/tensor calculus support.
3. Adding tests.
4. Adding documentation on use.
5. Publishing a final version to PyPI.

This project has a somewhat some minimal design and needs some involved
implementation work, and will require interacting with the mentors to flesh
out and work through.

* Required knowledge: Python (intermediate level) and calculus
* Difficulty level: easy
* Potential mentors: Prasun Anand and Hameer Abbasi
