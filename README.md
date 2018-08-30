# uarray - Universal Array Interface

[![Join the chat at https://gitter.im/Plures/uarray](https://badges.gitter.im/Plures/uarray.svg)](https://gitter.im/Plures/uarray?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Introduction

NumPy has become very popular as an array object --- but it implements
a very specific "kind" of array which is sometimes called a fancy
pointer to strided memory. This model is quite popular and has allowed
SciPy and many other tools to be built by linking to existing code.
Over the past decade, newer hardware including GPUs and FPGA, newer
software systems (including JIT compilers and code-generation systems)
have become popular.  Also new "kinds" of arrays have been created or
contemplated including distributed arrays, sparse arrays, "unevaluated
arrays", "compressed-storage" arrays, and so forth.  Quite often, the
downstream packages and algorithms that use these arrays don't need
the implementation details of the array.  They just need a set of basic
operations to work (the interface).

The goal of *uarray* is to constract an interface to a general array
concept and build a high-level multiple-dispatch mechanism to
re-direct function calls whose implementations are dependent on the
specific kind of array.  The desire is for down-stream libraries to be
able to use/expect `uarray` objects based on the interface and then have
their implementation configurable.  On-going discussions are happening
on the NumPy mailing list in order to retro-fit NumPy as this array
interface.  *uarray* is an alternative approach with different
contraints and benefits.


Python array computing needs multiple-dispatch.  Ufuncs are
fundamentally multiple-dispatch systems, but only at the lowest level.
It is time to raise the visibility of this into Python.  This effort
differs from [XND](https://xnd.io/) in that XND is low-level and
cross-langauge.  The *uarray* is "high-level" and Python only.  The
concepts could be applied to other languages but we do not try to
solve that problem.

Our desire with *uarray* is to build a useful array interface for Python
that can help library writers write to a standard interface while
allowing backend implementers to innovate in performance.  This effort
is being incubated at Quansight Labs which is an R&D group inside of
Quansight that hires developers, community/product managers, and
tech-writers to build and maintain shared open-source infrastructure.
It is funded by donations and grants.  The efforts are highly
experimental at this stage and we are looking for funding for the
effort in order to make better progress.


## Potential Usecases

* Dask (source: conversation w/ @mrocklin)
  * Optimize expressions before turning to graph (reduces size of graph, removes intermediaries) https://github.com/dask/dask/issues/2538 https://github.com/dask/dask/issues/3514 https://github.com/dask/dask/pull/3549 https://github.com/dask/dask/issues/746 https://github.com/dask/dask/pull/2608
  * More intelligent automatic chunking optimizations based on operations (https://github.com/dask/dask/issues/3864) (UK Met office might be interested in this) 
* xarray
  * Use for lazy operations to optimize https://github.com/pydata/xarray/issues/2298 https://github.com/pydata/xarray/pull/2302
* numba
  * support array optimizations on array like objects (source: conversation w/ @sklam) 
  * parallelization of array expressions https://github.com/numba/numba/issues/2432
* xnd
  * Generate optimized fused code outside of numba decorator
* probabilistic programming
  * Similar API to pymc4 (https://sharanry.github.io/post/eight-schools-model/) but not tied to tensorflow (can run on TF, numpy, pytorch)
* SciPy
  * Add GPU backend
* [datatable](https://github.com/h2oai/datatable) (API: https://github.com/h2oai/datatable/issues/696)
  * Optimize expression tree, use with other backends 
* [awkward-array](https://github.com/scikit-hep/awkward-array) (API: https://github.com/scikit-hep/awkward-array/blob/master/binder/array-types.ipynb)
  * Use with other backends

## References

- [NEP 18 — A dispatch mechanism for NumPy’s high level array functions](http://www.numpy.org/neps/nep-0018-array-function-protocol.html)

- [[Numpy-discussion] Proposal to accept NEP-18, __array_function__ protocol](https://mail.python.org/pipermail/numpy-discussion/2018-August/078578.html)

- Blog posts by Matthew Rocklin
  - [Beyond Numpy Arrays in Python](http://matthewrocklin.com/blog/work/2018/05/27/beyond-numpy)
  - [Summer Student Projects 2018](http://matthewrocklin.com/blog/work/2018/03/20/summer-projects)

- [Massiv: Efficient Haskell Arrays featuring Parallel computation](https://github.com/lehins/massiv)

- [Effective data parallel computation using the Psi calculus](https://paperpile.com/app/p/ad22b033-10cc-0f45-8c1d-05014496baee) 

- MatchPy, pattern matching
  - [Python library](https://github.com/HPAC/matchpy)
  - ["Non-linear Associative-Commutative Many-to-One Pattern Matching with Sequence Variables" - Manuel Krebber](https://arxiv.org/abs/1705.00907)
  
 - Magne Haveraaen - head of [Bergen Language Design Laboratory](https://bldl.ii.uib.no/)
   - [Specification of Generic APIs, or: Why Algebraic May Be Better Than Pre/Post](https://www.ii.uib.no/~anya/papers/bagge-haveraaen-hilt14-apispec.pdf)
     - algebraic specifications have history in CS
     - [Specification techniques for data abstractions - 1975](http://csg.csail.mit.edu/CSGArchives/memos/Memo-117.pdf)
       - groups of operations can be partitioned by whether they create class we care about, transform it, or create other class. This corresponds to some of our taxonomy of NP methods, those operations which create NP arrays, transform them, or turn them into something else. Another good way to think about array library. We have operations that take things external and turn them into abstract arrays (reading existing data, creating lazily from sequence),  operations that transform arrays (MoA operations), and then operations which leave the system (writing to storage, making concrete). ![](https://user-images.githubusercontent.com/1186124/44615089-f3e1e680-a7fe-11e8-9075-d8990ff44691.png)
   - [An array API for finite difference methods.](https://paperpile.com/app/p/fc16d058-1ac9-0296-af0d-87e75234458d)
   
