# symarray - Symbolic Array

symarray is a packages that facilitates creating verbatim array
expressions from Python native expressions.

Use cases:

+ The verbatim array expressions can be optimized using tools like
  uarray and evaluated using different array backends such as numpy,
  xnd, etc.

Definitions:

+ An array is a mapping of indices to items.
+ Array items are arbitrary objects (scalars, arrays, structures, etc)
  that are stored in memory at specific locations.
+ The storage locations of items are represented as single integers
  called pointers.
+ Array items have types. Item type carries information how to
  interpret the item value in different operations as well as how much
  memory-width is needed to store a particular item value.
+ Array shape is a structure that defines a mapping between array
  indices and pointer values, call it index-pointer mapping or gamma
  function.

Practicalities:

+ An array index is represented as a sequence of integers.
+ The origin of pointer values is arbitrary. Pointer value may be a
  memory address, or it may be an integer offset from some fixed base
  value.
+ Array items can be assumed to have fixed memory-width, in
  general. If this would not be a case, for instance, in the case of
  arrays containing items having different memory-widths, then one can
  construct an array of pointers (all pointers have the same
  memory-width) that values are offsets to the actual locations of the
  array items.

An array expression consists of the following objects and operations:

+ Array - represents an array with given shape, a scalar is defined as
  an array with empty shape.
+ element-wise operations: + - * / ** // %
+ indexing operations: indexing, slicing, etc.
+ reordering operations: advanced indexing, transpose, rotate, etc.
+ reduce operations: inner product, sum along given axis, etc.
+ tensor operations: outer product, outer sum, etc.

Notes:

+ When array shapes differ in element-wise operations then the
  validity of the expression is defined by broadcasting rules that are
  to be applied before evaluating element-wise operations.
+ Broadcasting produces new array shape that has many-to-one
  index-pointer mapping.
+ Element-wise operations produce new arrays that require memory
  allocation (and processing resources).
+ Indexing operations produce new array shapes w/o requiring memory
  allocations.
+ Reordering operations either produce new arrays or add parameters to
  array shapes.
+ Reduce and tensor operations produce new arrays that require memory
  allocation. In reduce and tensor operations the memory footprint is
  smaller and larger, respecitvely, than the memory footprint of the
  operands.

Target:

    N = Symbol('N')
	M = Symbol('M')
	k = Symbol('k')
    m = Symbol('m')
    a = Array('a', shape=NDShape((N, M)))
	b = a + 2
    expr = a[k].inner(a[m].outer(b[0])[n])

Current state:

    >>> from symarray import NDShape, Integer
    >>> n1 = Integer('n1')
    >>> n2 = Integer('n2')
    >>> n3 = Integer('n3')
    >>> 
    >>> # Shape of a 3-dimesional array
    ... s3 = NDShape((n1, n2, n3), offset=2000, itemsize=8)
    >>> print(s3)
    NDShape(dims=(n1, n2, n3), strides=(n1 * n2, n2, 1), offset=2000, itemsize=8)
    >>> 
    >>> # Get the pointer the value of array item with index (i1,i2,i3):
    ... i1 = Integer('i1')
    >>> i2 = Integer('i2')
    >>> i3 = Integer('i3')
    >>> p = s3(i1,i2,i3)
    >>> print(p)
    2000 + 8 * i1 * n1 * n2 + 8 * i2 * n2 + 8 * i3
    >>> 
    >>> # The shape of a subarray
    ... j1 = Integer('j1')
    >>> j2 = Integer('j2')
    >>> j3 = Integer('j3')
    >>> s2 = s3[i1,:,i3:j3]
    >>> print(s2)
    NDShape(dims=(n2, -i3 + j3), strides=(n2, 1), offset=2000 + 8 * i1 * n1 * n2 + 8 * i3, itemsize=8)
    >>>

