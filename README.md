# uarray - Universal Array Interface

## Introduction

NumPy has become very popular as an array object --- but it implements
a very specific "kind" of array which is sometimes called a fancy
pointer to strided memory. This model is quite popular and allowed
SciPy and many other tools to be built by linking to existing code.
Over the past decade, newer hardware including GPUs and FPGA, newer
software systems (including JIT compilers and code-generation systems)
have become popular.  Also new "kinds" of arrays have been created or
contemplated including distributed arrays, sparse arrays, "unevaluated
arrays", "compressed-storage" arrays, and so forth.  Quite often, the
downstream packages and algorithms that use these arrays don't need
the implementation details of the array.  They just a set of basic
operations to work (the interface).  The goal of uarray is to
constract an interface to a general array concept and build a
high-level multiple-dispatch mechanism to re-direct function calls
whose implementations are dependent on the specific kind of array.
The desire is for down-stream libraries to be able to use/expect
uarray objects based on the interface and then have their
implementation configurable.  On-going discussions are happening on
the NumPy mailing list in order to retro-fit NumPy as this array
interface.  uarray is an alternative approach with different
contraints and benefits.

## Discussions

[UArray Gitter channel](https://gitter.im/Plures/uarray)
