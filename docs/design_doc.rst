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

To execute a graph, we also need a compilation context. This is a mapping
from node names to functions which return a replacement node or
`NotImplemented`.
If they return a node, that node is replaced, otherwise it is kept as is.

To execute, we keep applying them, anywhere they match in the graph,
until they all return ``NotImplemented``.

For example, let's say we have a a graph like this:

.. code:: python

    initial = Node('add_int', [Node('int', [1]), Node('int', [2])])

And we would like to evaluate it by adding the integers, to a graph that
looks like this:

.. code:: python

    Node('int', [3])

We would define a compilation context like this:

.. code:: python

    def replace(node):
        if len(node.args) != 2 \
                or node.args[0].name != 'int' \
                or node.args[1].name != 'int':
            return NotImplemented
        return Node('int', [node.args[0].args[0] + node.args[1].args[1]])

    context = {
        "add_int": replace
    }


Then we could compile the expression using that context:

.. code:: python

    >>> compile(context, initial)
    Node('int', [3])


Creating Compilation Contexts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Often we would like to define multiple functions in different places
that each cover a different case of replacing a node. We can create
a new function that combines these two by introducing a ``ChainCallable``
structure (inspired by ``collections.ChainMap``), that could look like this:


.. code:: python

    class ChainCallable:
        def __init__(self, *callables):
            self.callables = callables

        def __call__(self, *args, **kwargs):
            for callable in self.callables:
                res = callable(*args, **kwargs)
                if res != NotImplemented:
                    return res
            return NotImplemented


So with this we could create two versions of `add_int`, depending one which adds python integers
and the other which creates a Python AST node based on two existing ast nodes that does addition:


.. code:: python


    context = collections.defaultdict(ChainCallable)

    @context['add_int'].callables.append
    def replace(node):
        if len(node.args) != 2 \
                or node.args[0].name != 'int' \
                or node.args[1].name != 'int':
            return NotImplemented
        return Node('int', [node.args[0].args[0] + node.args[1].args[1]])


    @context['add_int'].callables.append
    def replace_python_ast(node):
        if len(node.args) != 2 \
                or node.args[0].name != 'python_ast' \
                or node.args[1].name != 'python_ast':
            return NotImplemented
        return Node('python_ast', [ast.Add(node.args[0].args[0], node.args[1].args[1])])


These two replacement also share a common point in that they both only execute if the args are a
certain type. We can generalize this by creating a ``NodeWithArgs`` class:

.. code:: python


    class NodeWithArgs:
        def __init__(self, arg_names, replacement):
            self.arg_name == arg_names
            self.replacement == replacement

        def __call__(self, node):
            args = node.args
            if len(args) != self.arg_names:
                return NotImplemented
            for actual_arg_name, required_arg_name in zip(args, self.arg_names):
                if required_arg_name is None:
                    continue
                if actual_arg_name != required_arg_name"
                    return NotImplemented
            return self.replacement(node)

Then we can rewrite the above with:


.. code:: python


    context = collections.defaultdict(ChainCallable)

    def replace(node):
        return Node('int', [node.args[0].args[0] + node.args[1].args[1]])

    context['add_int'].callables.append(NodeWithArgs(['int', 'int']), replace)


    def replace_python_ast(node):
        return Node('python_ast', [ast.AddNode(node.args[0].args[0], node.args[1].args[1])])

    context['add_int'].callables.append(NodeWithArgs(['python_ast', 'python_ast']), replace)


Different modules will also likely want to have their own context and then the user can compose those contexts
(we can introduce a new class here).´

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

    context = {'apply': replace}

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
