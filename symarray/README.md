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



