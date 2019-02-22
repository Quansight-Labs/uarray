# `uarray` - Universal Array Interface. This is experimental and very early research code. Don't use this.

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

```bash
pip install uarray
```

```bash
conda install -c conda-forge -c uarray uarray
```

## Usage

Debugging tips:

- Call `visualize_progress(expr)` see all the replacement steps in order. Useful if you hit an exception
  to see the last computed state of the expression. You can also call `visualize_progress(expr, clear=False)`
  to see every stage in it's own output, although this uses a lot of screen space and will slow down your browser.
- In the tests, if you er

## Design

### Dispatching, core

In `uarray` we talk about two things, "types" and the "values" inside of them:

- Instances of `uarray.dispatch.Box` (or subclass) aka "**Types**" aka "Expressions"
  - Has a mutable `value` key which points to it's "**value**"
  - Has a `_replace(new_value)` method which returns a clone with the value changed.
  - Examples of this include:
    - The natural number 123: `Nat(123)`
    - An abstraction that maps `Nat(0)` to `Bool(True)` and `Nat(1)` to `Bool(False)`: `Abstraction((Bool(True), Bool(False))`
    - The same abstraction, represented differently: `Abstraction.create(lambda n: n.equals(Nat(0)), Nat(None))`
- Everything else aka "**Values**". We define a number of `functools.singledispatch` functions on these:
  - `key(val) -> object`: returns the key of the value. The default implementation is `return type(val)`.
  - `children(val) -> Iterable[Box]`: returns the "child" **types**. By default this is `return ()`.
  - `map_children(val: T, fn) -> T`: Returns a copy of the value with new children based on the mapping function.
  - `concrete(val) -> bool`: Concrete values are those that won't be replaced into other values. They are things like `Pair` or `ArrayData`, etc. I explain why we need this later on. Default is `True`.

So we see that a type contains one value. And a value can contain 0 or more types.

Alongside these data structures we also build up **replacements** which map a `Box` to a new `Box`. Replacements are partial functions, in the sense that they can also return `NotImplemented` to say it doesn't want to replace the box.

On top of that, we build a **context** which is a mapping of keys to replacements.

To try to replace a box, we look up the `key` of it's `value` in the context and apply that replacement to itself. If we get back `NotImplemented` we can't replace that box, otherwise we get back it's replacement.

We keep replacing a box, and the `children` of it's value, until no more replacement succeed.

### Dispatching, applied

This forms a solid base, but we had some more abstraction on top to cover the different types of **values** we care about. Note that the core system doesn't require any of these abstractions, and others could invent their own and define replacement on them as they wish and they will work together. So what kind of values do we care about?

- Base python values, like `int`, `numpy.ndarray`, or `ast.AST`. These have no children and are essentially opaque from uarrays perspective. It can't see inside them or replace inside of them. They are the leaf nodes.
- Instances of `Operation` which have a `name` and a number of `args`. The name is (usually) a function and the args are arguments for that function. Type wise, the `args` should be valid arguments for the function, and the value it returns should be the same type as this value's type.
  - For example the `Nat` type has a `__add__(self, other: Nat) -> Nat` method defined. So we could have an operation like `Nat(Operation(Nat.__add__, (Nat(1), Nat(2))))` that represents calling this method.
  - They also have a `concrete` argument which refers to if the Operation should ever
    be replaced by itself, or if is "concrete".

The reason we need to know whether values are `concrete` is that in some replacements we need to know "Will this value _ever_ become some type? i.e. Not only is that type right now, but will a replacement happen that will turn it into some type?"

For example, we use this when defining `List` operations. Sometimes their values are Python tuples of the values inside the list. But other times they are a more abstract mapping from the index to the value. So when we replace a `concat` operation on lists, we have to know which type is inside, to know which definition to use:

```python
@register(ctx, List.concat)
def concat(self: List[T_box], length: Nat, other: List[T_box]) -> List[T_box]:
    if isinstance(self.value, tuple) and isinstance(other.value, tuple):
        return self._replace(self.value + other.value)
    if concrete(self.value) and concrete(other.value):
        return List.from_function(
            lambda i: i.lt(length).if_(self[i], other[i - length])
        )
    return NotImplemented
```

The idea is that if it's a tuple, we know how to implement this. Otherwise, we revert to the general definition, based on indexing. This would still work if it was a tuple, but it wouldn't be as efficient and result in a messier graph. But the key is that we need to know if the value is `concrete` to know whether to use the default implementation. Otherwise, we might replace it too early, and it might become a tuple later, and then we used the "wrong" replacement.

### FAQ

Q: Why do we use classes for things like MoA or List instead of just functions>
A: In an earlier iteration of this project, everything was just a function and we didn't have any classes that combined functionality. It started this way because it's simpler to understand how multi dispatching works on functions with arguments, instead of methods. However, conceptually we still had to think about the "types" of data, meaning what functions are allowed on them. Python represents this concept with classes, so we use them. Practically, it provides a bunch of benefits:

- Allows better UX by using more of Python's syntax. We can override dunder methods to allow
  calling objects, getitem, or addition. This makes the usage less verbose and easier to read.
- Allows namespacing related functionality under one roof. For example, Mathematics of Arrays
  defines a number of functions. We would like to be able to "work in this world", which
  is easy if all the methods are accessible from a `MoA` class. We can use modules for the same purpose, but I find it easier to deal with importing a class and using it's methods
  instead of importing a module.

## Development

```bash
conda create -n uarray python=3.7
conda activate uarray

flit -f udispatch.toml install --symlink
flit -f uarray.toml install --symlink
flit -f umoa.toml install --symlink
flit -f umoa_parser.toml install --symlink
flit -f unumpy.toml install --symlink
flit -f uvisualize.toml install --symlink
```

### Testing

```bash
py.test
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
