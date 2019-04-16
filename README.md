# `uarray` - Universal Array Interface. This is experimental and very early research code. Don't use this.

[![Join the chat at https://gitter.im/Plures/uarray](https://badges.gitter.im/Plures/uarray.svg)](https://gitter.im/Plures/uarray?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/Quansight-Labs/uarray/master?urlpath=lab/tree/notebooks/NumPy%20Compat.ipynb) [![Build Status](https://dev.azure.com/Quansight-Labs/uarray/_apis/build/status/Quansight-Labs.uarray?branchName=master)](https://dev.azure.com/Quansight-Labs/uarray/_build/latest?definitionId=1&branchName=master) [![PyPI](https://img.shields.io/pypi/v/uarray.svg?style=flat-square)](https://pypi.org/project/uarray/)

<img src="docs/logo.png" width="20em" alt="uarray logo">

- [Documentation](https://uarray.readthedocs.io/en/latest/)
- [Road Map](https://github.com/orgs/Quansight-Labs/projects/1)
- [Future Meetings](https://calendar.google.com/calendar/embed?src=quansight.com_cg7sf4usbcn18gdhdb3l2c6v1g%40group.calendar.google.com&ctz=America%2FNew_York)
- [Meeting Notes](https://github.com/Quansight-Labs/uarray/wiki/Meeting-Notes)
- [References](https://github.com/Quansight-Labs/uarray/wiki/References)
- [Papers](https://paperpile.com/shared/fHftX5)

## Background

NumPy has become very popular as an array object --- but it implements
a very specific "kind" of array which is sometimes called a fancy
pointer to strided memory. This model is quite popular and has allowed
SciPy and many other tools to be built by linking to existing code.

Over the past decade, newer hardware including GPUs and FPGA, newer
software systems (including JIT compilers and code-generation systems)
have become popular. Also new "kinds" of arrays have been created or
contemplated including distributed arrays, sparse arrays, "unevaluated
arrays", "compressed-storage" arrays, and so forth. Quite often, the
downstream packages and algorithms that use these arrays don't need
the implementation details of the array. They just need a set of basic
operations to work (the interface).

The goal of _uarray_ is to construct an interface to a general array
concept and build a high-level multiple-dispatch mechanism to
redirect function calls whose implementations are dependent on the
specific kind of array. The desire is for down-stream libraries to be
able to use/expect `uarray` objects based on the interface and then have
their implementation configurable. Ongoing discussions are happening
on the NumPy mailing list in order to retrofit NumPy as this array
interface. _uarray_ is an alternative approach with different
contraints and benefits.

Python array computing needs multiple-dispatch. Ufuncs are
fundamentally multiple-dispatch systems, but only at the lowest level.
It is time to raise the visibility of this into Python. This effort
differs from [XND](https://xnd.io/) in that XND is low-level and
cross-language. The _uarray_ is "high-level" and Python only. The
concepts could be applied to other languages but we do not try to
solve that problem with this library. XND can be _used_ by some
implementations of the uarray concept.

Our desire with `uarray` is to build a useful array interface for Python
that can help library writers write to a standard interface while
allowing backend implementers to innovate in performance. This effort
is being incubated at Quansight Labs which is an R&D group inside of
Quansight that hires developers, community/product managers, and
tech writers to build and maintain shared open-source infrastructure.
It is funded by donations and grants. The efforts are highly
experimental at this stage and we are looking for funding for the
effort in order to make better progress.

## Status

This project is in active development and not ready for production use. However, you can install it with:

```bash
pip install uarray
```

or

```bash
conda install -c conda-forge -c uarray uarray
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for more information on how to contribute to `uarray`.
