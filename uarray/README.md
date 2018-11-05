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

### Arrays (and contents and callables)

_Note: The relevent code for this section is in the `uarray/core.py` file._

TODO: Look at other names for contents and callables. Contents could become Value, if we change Value
as it is to just be typed versions of itself. aka have Integer and String but not base Value symbol.

There are many ways we could implement the concept of a multi dimensional array in MatchPy.
We are interested in ways to do this that will let us express take high level descriptions of array operations,
like those present in Lenore Mullin's these, A Mathematics of Arrays (MoA), and replace them with simpler expressions.
That work treats arrays as having two things, a shape and a function to go from an index to a value.

Here we think about arrays as a `Sequence(length, getitem)`, a `Scalar(content)`, or any form that can be replaced into these forms.
Let's start with an example, using these expressions, then we can get into the weeds of what this all means.

```python
s = uarray.Scalar(uarray.Value(10))

assert uarray.replace(uarray.Contents(s)) == uarray.Value(10)
```

We see that a `Scalar` just wraps some underlying thing, we call the contents. We can extract
out it out with the `Contents` operator. Now let's look at a `Sequence`:

```python
class Always(matchpy.Operation):
    name = "Always"
    arity = matchpy.Arity(1, True)

a = uarray.Sequence(
    uarray.Value(5),
    Always(s)
)

assert uarray.replace(uarray.Length(s)) == uarray.Value(5)
assert uarray.replace(uarray.GetItem(a)) == Always(s)
```

Here we define `a` to be a sequence of length 5 that contains all scalars of value 10.
We can also understand this as a one dimensional array, like `np.array([10, 10, 10, 10, 10])`.

We see that a sequence has two items we can extract out, the `GetItem`
and the `Length`. But what is this `Always` operator? Well we just defined it.
The getitem part of the sequence should be a callable that takes in an index of type
contents and returns an array. So let's make `Always` a callable that works like this:

```python
register(uarray.Call(Always(w.x), w.idx), lambda x, idx: x)
```

A callable is any expression that you can use `uarray.Call` on it as the first argument,
and it's arguments as the rest of the arguments. It should replace this form into it's result.
In this case, we have a simple `Callable` that takes one argument and just returns what is inside of it.
i.e. it doesn't matter what it is called with, it always returns it's first operand.

Now, we can get the callable from the array and call it on an index:

```python
idx = uarray.Value(2)

indexed_a = uarray.Call(
    uarray.GetItem(a),
    idx
)

assert uarray.replace(indexed_a) == s
```

This is how we index arrays in uarray. We extract out their callables and call them with the index. The `Index` function in Mathematics of Arrays (or in NumPy) allows you to index an array with a vector, just like how in NumPy you can index an array with a tuple of indices.

How does it work? If you look at it's defintion in `uarray/moa.py` you will see it uses this pattern above once for each index in the vector.

A mistake I often make is giving an expression of the wrong type to some expression.
For example, what if I defined an array like this:

```python
uarray.Sequence(uarray.Scalar(uarray.Value(10)), Always(Scalar(10)))
```

Can you spot what is wrong? The length of the sequence is an Array not a contents!
So this should instead be:

```python
uarray.Sequence(uarray.Value(10), Always(Scalar(10)))
```

What do I mean "should"? Will this give an error? An exception? Most likely it will not.
You will just end up with some long expression down the line that cannot be reduced
because it has the wrong type inside. It's like casting a pointer to another type in C
and then reading in the values. It won't error when you cast the pointer, but the contents
of it doesn't have the write structure to be meaningful.

The moral is
**always understand what classes of expressions your expression takes and don't pass those of another class.**

TODO: Enforce this somehow. We could possibly use python types to define these different
classes and have each expression subclass subclass also from this Python type. This could
get static type checking (possibly). But it comes at the expense of introducing a Python
type hierarchy where we don't really need one, just for MyPy.

### Explaining Callables
