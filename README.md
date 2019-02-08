# uarray - Universal Array Interface. This is experimental and very early research code. Don't use this.

[![Join the chat at https://gitter.im/Plures/uarray](https://badges.gitter.im/Plures/uarray.svg)](https://gitter.im/Plures/uarray?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/Quansight-Labs/uarray/master?urlpath=lab/tree/notebooks/NumPy%20Compat.ipynb) [![Build Status](https://dev.azure.com/teoliphant/teoliphant/_apis/build/status/Quansight-Labs.uarray)](https://dev.azure.com/teoliphant/teoliphant/_build/latest?definitionId=1) [![PyPI](https://img.shields.io/pypi/v/uarray.svg?style=flat-square)](https://pypi.org/project/uarray/)

- [Road Map](https://github.com/Quansight-Labs/uarray/projects/2)
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

The goal of _uarray_ is to constract an interface to a general array
concept and build a high-level multiple-dispatch mechanism to
re-direct function calls whose implementations are dependent on the
specific kind of array. The desire is for down-stream libraries to be
able to use/expect `uarray` objects based on the interface and then have
their implementation configurable. On-going discussions are happening
on the NumPy mailing list in order to retro-fit NumPy as this array
interface. _uarray_ is an alternative approach with different
contraints and benefits.

Python array computing needs multiple-dispatch. Ufuncs are
fundamentally multiple-dispatch systems, but only at the lowest level.
It is time to raise the visibility of this into Python. This effort
differs from [XND](https://xnd.io/) in that XND is low-level and
cross-langauge. The _uarray_ is "high-level" and Python only. The
concepts could be applied to other languages but we do not try to
solve that problem with this library. XND can be _used_ by some
implementations of the uarray concept.

Our desire with _uarray_ is to build a useful array interface for Python
that can help library writers write to a standard interface while
allowing backend implementers to innovate in performance. This effort
is being incubated at Quansight Labs which is an R&D group inside of
Quansight that hires developers, community/product managers, and
tech-writers to build and maintain shared open-source infrastructure.
It is funded by donations and grants. The efforts are highly
experimental at this stage and we are looking for funding for the
effort in order to make better progress.

## Status

This project is in active development and not ready for production use. However, you can install it with:

### PyPI

```bash
pip install uarray
```

### Conda

```bash
conda install -c conda-forge -c uarray uarray
```

## Usage

Debugging tips:

- Call `visualize_progress(expr)` see all the replacement steps in order. Useful if you hit an exception
  to see the last computed state of the expression. You can also call `visualize_progress(expr, clear=False)`
  to see every stage in it's own output, although this uses a lot of screen space and will slow down your browser.
- In the tests, if you er

## Development

```bash
conda create -n uarray python=3.7
conda activate uarray
pip install -r requirements.dev.txt
flit install --symlink
```

### Testing

```bash
mypy uarray
# python extract_readme_tests.py
py.test uarray/
```

To re-run notebooks (their outputs are checked in the tests):

```bash
jupyter nbconvert --to notebook --inplace --execute notebooks/Paper\ Problem.ipynb
```

### Releases

Make sure to update `pyproject.toml` and `.conda/meta.yaml` to the
correct version on a new release.

Flit makes `pypi` releases quite simple. Flit will use your
`~/.pypirc` or environment variables `FLIT_USERNAME`, `FLIT_PASSWORD`,
and `FLIT_INDEX`.

```bash
flit publish
```

Conda releases use the `.conda/meta.yaml` recipe.

```bash
conda install conda-build anaconda-client
anaconda login
conda build -c conda-forge .conda/
anaconda upload --user uarray <path to conda build>
```
