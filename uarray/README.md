# uarray

[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/Quansight-Labs/uarray/master?urlpath=lab/tree/uarray/NumPy%20Compat.ipynb)

## Development

The code relies on Python 3.6+ and `matchpy`. Besides that, we use NumPy to define some
interop code and also rely on JupyterLab and the like for development. To get a nice
package of what you need, feel free to use the included `environment.yml`.

```bash
conda env create -f environment.yml
conda activate uarray
```

This code hasn't been published yet on PyPi or Conda.

## Internals

Unlike other libraries I have worked on in Python, much of the design of uarray has been focused on the
internal representations instead of the user facing interfaces. From a users perspective, most of these details
are hidden. If you use the `optimize` decorator or even the lower level `LazyNDArray` wrapper, you get back some Python function
you can call that should do what you want and should be fast or efficient in some way. But that isn't actually the interesting or powerful
part of the system. Instead, it's meant to give a framework where users can easily add to the core working internals and the actually
"core" of the system is very minimal. Why this approach? To allow faster iteration as things evolve, without having to rewrite everthing.
I.e. to be able to support a wide array of paradigms of input and output.

So in this section, I want to give an overview of internals of uarray in an attempt to make it extendable by others. I will try to **bold**
any tips that can help avoid subtle errors. Eventually, it would be nice if some these tips were all verified as you develop automatically.

### MatchPy

_Note: The relevent code for this section is in the `uarray/machinery.py` file._

Fundamentally, uarray is just a set of patterns on top of the [MatchPy](https://github.com/HPAC/matchpy) pattern matching system in Python.

We start with the `matchpy.Expression` class. Most of uarray is subclasses of either `matchpy.Symbol` or `matchpy.Operation`, both of which
are subclasses of `matchpy.Expression`. Every `Symbol` subclasses contain a `name` which is a Python object. They are the leaves of the expression tree.
Whereas each `Operation` subclass is initialized with a number of other `Expressions`s. These are stored on the `operands` attribute of the instance.

TODO: Make `uarray.Value` use just `name`

Here is an example of creating a recursive list in matchpy:

```python
import matchpy

class Value(matchpy.Symbol):
    pass

class Nil(matchpy.Operation):
    name = "Nil"
    arity = matchpy.Arity(0, True)

class Cons(matchpy.Operation):
    """
    Cons(value, list)
    """
    name = "Cons"
    arity = matchpy.Arity(2, True)

class List(matchpy.Operation):
    """
    List(*values)
    """
    name = "List"
    arity = matchpy.arity(0, False)

nil_list = Nil()
assert not nil_list.operands

v = Value(1)
assert v.name == 1

a = Cons(v, Nil())
assert a.operands == [v, Nil()]

b = List(v)
assert v.operands == [v]
```

Then in uarray we define one global `matchpy.ManyToOneReplacer` that holds a bunch of replacement rules, to take some expression tree and replace it with another.
We define a helper `register` function that takes in an expression to match, some custom contraints, and the replacement function.

We also define two objects, `w` and `ws` that return [`matchpy.Wildcard`](https://matchpy.readthedocs.io/en/latest/api/matchpy.expressions.expressions.html#matchpy.expressions.expressions.Wildcard)s.
If you get an attribute from them, it returns a wildcard with that name. This is a way to extract out some part of the matched pattern and pass it into
the function so that you can use it to return a new pattern. The difference between the two is that `w` creates wildcard that match one and only
one expression, while `ws` matches wildcards that return 0 or more expression. They are like `.` and `.*` in regex land.

Let's show how this works in this example, by adding a rule to turn Lists expression into nested Cons expressions:

```python
import uarray

# base case
uarray.register(List(), lambda: Nil())
uarray.register(List(uarray.w.x, uarray.ws.xs), lambda x, xs: Cons(x, List(*xs)))
```

To use the global replacer on an expression, we provide the `replace` function. It takes in some expression and keep applying replacement rules
that match (in arbitrary order) until it cannot find any more to replace.

Two things to note about this. If two replacement rules could match the same expression, then which one is executed is not fixed. Therefore,
there **should not be multiple replacement rules registered that could match the same pattern**. If there are, you might get non deterministic compilation.
The other thing is that replacement rules are fundementally one way. They are not equivalencies. So it becomes helpful to think about
**what are the types of expressions I have when I start and what are the types of expression I have when everything has been replaced**.
In this case, we start with higher level `List` forms and end up with lower level nested `Cons` forms.

Let's see this in action:

```python
assert uarray.replace(List()) == Nil()
assert uarray.replace(b) == a
```

Since each replacement happens in a sequence, it is often helpful to look at not just the final replaced form, but all the intermediate forms as well.
For that, we provide the `replace_scan`, which returns an iterable of all the replacements. This can also be helpful to use to debug infintely replacing forms,
because it is lazily evaluted.

TODO: add `replace_scan` and add original value as output

```python
assert list(uarray.replace_scan(List())) == [List(), Nil()]
assert list(uarray.replace_scan(b)) == [List(v), Cons(v, List()), Cons(v, Nil())]
```

One interesting thing to note here is that as the expression moves from what the user enters (`List(x, ...)`)
to the final form (`Cons(a, Cons(...))`) we move through intermediate forms that have both types of expressions.
So it's also helpful to not only think about what kinds of forms should we start with and what kinds should we end with,
but **making sure that the expression still has a meaningful form as it progresses**. This helps reasonsing about
intermediate forms to make sure they are "correct" in the sense that they express what you want them to. Otherwise, it
can be hard to diagnose where things go wrong and reason about the state.

There is one last note about our use of Matchpy. When you construct any form in MatchPy, you can also provide a `variable_name` for it.
Then you can use the `matchpy.substitute` function to replace any values with that `variable_name` with another expression. For example:

```python
v_p = Value(None, variable_name="A")
assert matchpy.substitute(Cons(v_p, Nil()), {"A": Value(1)}) == Cons(Value(1), Nil())
```

### Arrays

_Note: The relevent code for this section is in the `uarray/core.py` file._

There are many ways we could implement the concept of a multi dimensional array in MatchPy.
We are interested in ways to do this that will let us express take high level descriptions of array operations,
like those present in Lenore Mullin's these, A Mathematics of Arrays (MoA), and replace them with simpler expressions.
That work treats arrays as having two things, a shape and a function to go from an index to a value.

Here we think about arrays as a `Sequence(length, getitem)`, a `Scalar(content)`, or any form that can be replaced into these forms.
Let's start with an example, using these expressions, then we can get into the weeds of what this all means.

```python
class Always(matchpy.Operation):
    name = "Always"
    arity = matchpy.Arity(1, True)

register(uarray.Call(Always(w.x), w.idx), lambda x, idx: x)

s = uarray.Scalar(uarray.Value(10))

a = uarray.Sequence(
    uarra.Value(5),
    Always(s)
)

idx = uarray.Value(2)

indexed_a = uarray.Call(
    uarray.GetItem(a),
    idx
)

assert uarray.replace(indexed_a) == s
```

Here we define `a` to be a sequence of length 5 that contains all scalars of value 10.

We can also understand this as a one dimensional array, like `np.array([10, 10, 10, 10, 10])`.

Then we get the 2nd value of a, which is a scalar (aka a 0D array) with value 10.

It get's a bit hairy, because to understand arrays, we also have to understand two other types of expressions, callables and contents.

So how do we construct these arrays?

What can we do with these arrays? Let's start with the second question. First, we introduce some
other operations that extract out the various parts of the array expressions, so that we can explain how they operate:

1. `Length(Sequence(length, getitem))` turns into `length`
2. `GetItem(Sequence(length, getitem))` turns into `getitem`
3. `Content(Scalar(content))` turns into `Content`

Then we really just have one operation we care about on `Sequences`s, which is getting an item. This should return a new Array:

4. `Call(Getitem(some_sequence), some_idx)` turns into another array

You probably have a bunch of questions right about now. Hopefully they will all get answered in the remaining part of this section.

Let's start with what does "turns into" mean? It just means it eventually should end up being that after replacement rules are executed.

Before we can go into how you create these array

You might have some questions about why we are using this form for arrays. Why don't we implement them closer to MoA does?
Like `Array(shape, indexing_fn)`? Two reasons:

1. Often it is simpler to think about indexing
