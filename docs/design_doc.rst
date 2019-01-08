``uarray``/"Mathematics of Arrays": Design
==========================================

Goals
-----

**Backend Developer**:

1. Target hardware and software backends, including:

   1. Deep Embedded DSLs (TensorFlow, ``llvmlite``)
   2. Simple Python functions (NumPy code that can be compiled with
      Numba)
   3. Python functions (Array protocol)

2. Provide precompiled high level operations

**Algorithm Developers**:

1. Implement array operations, including those in:

   1. NumPy
   2. SciPy
   3. Mathematics of Arrays

**User**:

1. Compose any algorithms and use with any backend.
2. Switch between precompiled and JIT compiled implementations of
   algorithms.

**``uarray`` Developer**

1. Prevent breaking changes in API over time
2. Make codebase understandable

Solution
--------

We create an an IR/embedded DSL for array expressions.

This language is based off of the lambda calculus and extensible from
the host language of Python.

The requirements of this language are:

-  Allow algorithm authors to create composite operations
-  Allow backends to translate any operation in a custom way, or use the
   default generic implementation
-  Be able to visualize the IR to understand it and to understand the
   process of compilation

Graph
~~~~~

The basic idea is a multiple dispatch system that can not evaluate terms
if no match is valid yet. In other dispatching systems in Python, if
there is no match, there is some base case or an exception is raised.
Here, we want to preserve the call, but not execute it, if we cannot
find a valid match.

Why? So that we can represent things like functions symbolically and
look at them before they are executed.

So we end up with a two stage process:

1. Build up execution as a graph
2. Execute the graph

..

    Why a graph and not a tree? For two reasons:

    1. Executing replacement on a graph is more efficient, because the
       total number of nodes is decreased. Each time you duplicate a
       value, the total number of nodes stays the same instead of
       increasing.
    2. Understanding it as a graph let's you implement variables more
       natively. Instead of each having a distinct name, they are all
       just different Python objects. So if two parts of the graph hold
       a reference to the same variable, that variable is not copied
       into the two parts, like it would be in a tree, but instead both
       point to it.

Each ``Node`` has a ``name`` (string) and a sequence of ``args``. Each
arg is either a ``Node`` or any other Python value.

To define how the graph executes, we register replacements for the
nodes. For each replacement, we define the ``name`` it operates on a
replacement function that should return a new node given the old node.
If it returns ``NotImplemented``, we look for other replacements to
call. The replacements are ordered so those that are registered later
and called first.

To execute, we keep applying them, anywhere they match in the graph,
until they all return ``NotImplemented``.

For example, let's say we have a a graph like this:

.. code:: python

    Node('add_int', [Node('int', [1]), Node('int', [2])])

And we would like to evaluate it by adding the integers, to a graph that
looks like this:

.. code:: python

    Node('int', [3])

We would register a replacement like this:

.. code:: python


    def replace(node):
        if len(node.args) != 2 \
                or node.args[0].name != 'int' \
                or node.args[1].name != 'int':
            return NotImplemented
        return Node('int', [node.args[0].args[0] + node.args[1].args[1]])

    register_replacement(
        'add_int',
        replace
    )

When we apply a ``Replacement`` to a graph, we mutate the graph to
contain the result of the replacement. Because we update the nodes in
place, if one node is updated that has two different parents, each will
see the new node as a child without having to keep track of all parent
nodes.

Lambda Calculus
~~~~~~~~~~~~~~~

To implement an untyped lambda calculus, we define a few nodes:

-  ``variable``: one argument, an optional human label (only for
   display, has not effect on computation)
-  ``abstraction``: two arguments, an argument name which is a variable
   and a body
-  ``apply``: two arguments, an abstraction and an argument to apply

We replace applications with the body of the application, with all
instances of the variable replaced by the arg. Could be defined like
this:

.. code:: python

    def replace(application):
        if len(application.args) != 2 or applications.args[0].name != 'application':
            return NotImplemented

        abstraction, arg = application.args
        
        arg_variable, body = abstraction.args

        if arg_variable == body:
            return arg

        # recursively apply to child args that are Nodes themselves, don't apply to literal args
        return Node(body.name, [Node('apply', [abstraction, arg]) if isinstance(arg, Node) else arg for arg in body.args])

    register_replacement('apply', replace)

Core Replacements
~~~~~~~~~~~~~~~~~

We would define a number of primitive types, like booleans and natural
numbers, and operations between them, like ``and``, ``multiply``, etc.

We would also define some control flow statements, like ``if`` and
looping over a natural number, which would behave like this in Python:

.. code:: python

    def nat_loop(initial, fn, n):
        val = initial
        for i in range(n):
            val = fn(i, val)
        return val

How are arrays implemented in this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First we start with lists. We define them as a node with all items in
them as their args, like this:

.. code:: python

    l = Node('list', [Node('int', [1]), Node('int', [2])])

We define a ``list_getitem`` node that takes a list and an index and
returns that item from the list.

A vector type is a list with a length associated, like this:

.. code:: python

    v = Node('vector', [Node('int', 2), l])

For a vector, we define a ``vector_extract_length`` and
``vector_extract_list`` that extracts out the list and length and list
from the vector.

Arrays in turn have:

-  a dtype which is retrieved with ``array_extract_dtype`` and can be
   any type
-  a shape retrieved with ``array_extract_shape``, which is a vector of
   integers
-  a indexing function, retrieved with ``array_extract_indexing``, which
   is an abstraction from a list of integers to any type

Related solutions
-----------------

-  Turn host language functions into DSL by introspecting `"Deeply
   Reifying Running Code for Constructing a Domain-Specific
   Language" <https://paperpile.com/app/p/9888f10b-dbd4-0d4d-82ea-ed95f0f18ec8>`__
