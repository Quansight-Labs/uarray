import typing
from .machinery import *
from .core import *
from .core.arrays import Array


T_cov = typing.TypeVar("T_cov")


@operation(name="ρ")
def Shape(a: ArrayType[T_cov]) -> ArrayType[NatType]:
    ...


@replacement
def _array_shape(
    shape: ShapeType, idx: IdxType[T_cov]
) -> DoubleThunkType[ArrayType[NatType]]:
    return lambda: Shape(Array(shape, idx)), lambda: VecToArray(shape)


@operation(name="ψ", infix=True)
def Index(indices: ArrayType[NatType], ar: ArrayType[T_cov]) -> ArrayType[T_cov]:
    ...


"""
Should indexing function map from lists or vectors?

    lists: dont need length! helps when destructing, dont have to recreat vectors everywhere

    vectors: simpler, dont need to think about other data type. Only need to define operations
    on vectors not lists.
"""


@replacement
def _array_index(
    indices_shape: ShapeType,
    indices_idx: IdxType[NatType],
    array_shape: ShapeType,
    array_idx: IdxType[T_cov],
) -> DoubleThunkType[ArrayType[T_cov]]:
    def pattern() -> ArrayType[T_cov]:
        return Index(Array(indices_shape, indices_idx), Array(array_shape, array_idx))

    def replacement_fn() -> ArrayType[T_cov]:
        indices_length = VecLength(indices_shape)
        new_shape = VecDrop(indices_length, array_shape)

        def index_fn(idx: ShapeType) -> T_cov:
            return Apply(array_idx, VecConcat(Array(indices_shape, indices_idx), idx))

        return Array(new_shape, abstraction(index_fn))

    return (pattern, replacement_fn)


@operation(name="red")
def Reduce(
    fn: CallableBinaryType[ArrayType[T], ArrayType[T], ArrayType[T]],
    initial_value: ArrayType[T],
    arr: ArrayType[T],
) -> ArrayType[T]:
    ...


@replacement
def _reduce(
    fn: CallableBinaryType[ArrayType[T], ArrayType[T], ArrayType[T]],
    initial_value: ArrayType[T],
    dim: NatType,
    first_shape: Int,
    rest_shape: typing.Sequence[NatType],
    array_index: IndexType[T],
) -> DoubleThunkType[ArrayType[T]]:
    def replacement_fn():
        value = initial_value
        for i in range(first_shape.value()):
            value = ApplyBinary(fn, value, Apply(array_index, List(Int(i))))
        return value

    return (
        lambda: Reduce(
            fn,
            initial_value,
            Pair(Vector(dim, List(first_shape, *rest_shape)), array_index),
        ),
        replacement_fn,
    )


# def _reduce_vector(fn, value, length, getitem):
#     for i in range(length.name):
#         value = ApplyBinary(fn, value, Apply(getitem, VectorToPair(Int(1), List(Int(i)))))
#     return value


# register(
#     ReduceVector(w("fn"), w("value"), Sequence(sw("length", Int), w("getitem"))),
#     _reduce_vector,
# )


# @operation(name="+", infix=True)
# def Add(l: CContent, r: CContent) -> CContent:
#     ...


# register(Add(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name + r.name))


# @operation(name="*", infix=True)
# def Multiply(l: CContent, r: CContent) -> CContent:
#     ...


# register(Multiply(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name * r.name))


# def wrap_binary(
#     fn: typing.Callable[[CContent, CContent], CContent]
# ) -> typing.Callable[[ArrayType, ArrayType], ArrayType]:
#     return lambda a, b: Scalar(fn(Content(a), Content(b)))


# @operation(name="π")
# def Pi(ar: ArrayType) -> ArrayType:
#     ...


# multiply = binary_function(wrap_binary(Multiply))


# def _pi(ar: ArrayType) -> ArrayType:
#     return ReduceVector(binary_function(wrap_binary(Multiply)), Scalar(Int(1)), ar)


# register(Pi(w("ar")), _pi)


# @operation(name="τ")
# def Total(ar: ArrayType) -> ArrayType:
#     ...


# register(Total(w("x")), lambda x: Pi(Shape(x)))


@operation(name="ι")
def Iota(n: ArrayType[NatType]) -> ArrayType[NatType]:
    """
    Iota(n) returns a vector of 0 to n-1.
    """
    ...


empty_indices: ListType[NatType] = List()


@replacement
def _iota(
    shape_index: ListType[NatType], array_index: IndexType[NatType]
) -> DoubleThunkType[ArrayType[NatType]]:

    return (
        lambda: Iota(Pair(Vector(Int(0), shape_index), array_index)),
        lambda: Pair(
            Vector(Int(1), List(Apply(array_index, empty_indices))),
            PythonUnaryFunction(ListFirst),
        ),
    )


# @operation(name="δ")
# def Dim(n: ArrayType) -> ArrayType:
#     ...


# register(Dim(w("x")), lambda x: Pi(Shape(Shape(x))))


# @operation(name="%")
# def Remainder(l: CContent, r: CContent) -> CContent:
#     ...


# register(Remainder(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name % r.name))


# @operation(name="//")
# def Quotient(l: CContent, r: CContent) -> CContent:
#     ...


# register(Quotient(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name // r.name))


# @operation(name="rav")
# def Ravel(n: ArrayType) -> ArrayType:
#     ...


# register(Ravel(Scalar(w("c"))), lambda c: Sequence(Int(1), Always(Scalar(c))))


# def _ravel_sequence(length: CContent, getitem: CGetItem) -> ArrayType:
#     a = Sequence(length, getitem)

#     inner_size = Content(Total(Apply(getitem, unbound_content())))

#     def new_getitem(idx: CContent) -> ArrayType:
#         this_idx = Quotient(idx, inner_size)
#         next_idx = Remainder(idx, inner_size)
#         return Apply(GetItem(Ravel(Apply(getitem, this_idx))), next_idx)

#     return Sequence(Content(Total(a)), unary_function(new_getitem))


# register(Ravel(Sequence(w("length"), w("getitem"))), _ravel_sequence)


# @operation(name="ρvec")
# def ReshapeVector(new_shape: CVectorCallable, vec: ArrayType) -> ArrayType:
#     ...


# def _reshape_vector_scalar(length: CContent, getitem: CGetItem) -> ArrayType:
#     return Scalar(Content(Apply(getitem, Int(0))))


# register(
#     ReshapeVector(VectorCallable(), Sequence(w("length"), w("getitem"))),
#     _reshape_vector_scalar,
# )


# def _reshape_vector_array(
#     new_length: CContent,
#     rest: typing.Iterable[ArrayType],
#     length: CContent,
#     getitem: CGetItem,
# ) -> ArrayType:
#     inner_size = Content(Pi(vector_of(*rest)))

#     def new_getitem(idx: CContent) -> ArrayType:
#         offset = Multiply(inner_size, idx)

#         def inner_getitem(inner_idx: CContent) -> ArrayType:
#             return Apply(getitem, Remainder(Add(inner_idx, offset), length))

#         return ReshapeVector(
#             VectorCallable(*rest), Sequence(inner_size, unary_function(inner_getitem))
#         )

#     return Sequence(new_length, unary_function(new_getitem))


# register(
#     ReshapeVector(
#         VectorCallable(Scalar(w("new_length")), ws("rest")),
#         Sequence(w("length"), w("getitem")),
#     ),
#     _reshape_vector_array,
# )


# @operation(name="ρ", infix=True)
# def Reshape(new_shape: ArrayType, array: ArrayType) -> ArrayType:
#     ...


# register(
#     Reshape(Sequence(w("length"), w("getitem")), w("array")),
#     lambda length, getitem, array: ReshapeVector(getitem, Ravel(array)),
# )


# @operation
# def BinaryOperation(
#     op: CallableBinaryType[ArrayType, ArrayType, ArrayType], l: ArrayType, r: ArrayType
# ) -> ArrayType:
#     ...


# # Both scalars

# register(
#     BinaryOperation(w("op"), Scalar(w("l")), Scalar(w("r"))),
#     lambda op, l, r: ApplyBinary(op, Scalar(l), Scalar(r)),
# )


# register(
#     BinaryOperation(w("op"), Scalar(w("s")), Sequence(w("length"), w("getitem"))),
#     lambda op, s, length, getitem: Sequence(
#         length,
#         unary_function(
#             lambda idx: BinaryOperation(op, Scalar(s), Apply(getitem, idx))
#         ),
#     ),
# )
# register(
#     BinaryOperation(w("op"), Sequence(w("length"), w("getitem")), Scalar(w("s"))),
#     lambda op, s, length, getitem: Sequence(
#         length,
#         unary_function(
#             lambda idx: BinaryOperation(op, Apply(getitem, idx), Scalar(s))
#         ),
#     ),
# )


# register(
#     BinaryOperation(
#         w("op"),
#         Sequence(w("l_length"), w("l_getitem")),
#         Sequence(w("r_length"), w("r_getitem")),
#     ),
#     lambda op, l_length, l_getitem, r_length, r_getitem: Sequence(
#         Unify(l_length, r_length),
#         unary_function(
#             lambda idx: BinaryOperation(
#                 op, Apply(l_getitem, idx), Apply(r_getitem, idx)
#             )
#         ),
#     ),
# )


# @operation
# def OmegaUnary(
#     function: CallableUnaryType[ArrayType, ArrayType], dim: CContent, array: ArrayType
# ) -> ArrayType:
#     ...


# # TODO: Make this invese. if 0 we should keep traversing
# def _omega_unary_sequence(
#     fn: CallableUnaryType[ArrayType, ArrayType], dim: CInt, array: ArrayType
# ) -> ArrayType:
#     if dim.name == 0:
#         return Apply(fn, array)
#     new_dim = Int(dim.name - 1)
#     return Sequence(
#         Length(array),
#         unary_function(
#             lambda idx: _omega_unary_sequence(
#                 fn, new_dim, Apply(GetItem(array), idx)
#             )
#         ),
#     )


# register(OmegaUnary(w("fn"), sw("dim", Int), w("array")), _omega_unary_sequence)


# @operation(infix=True)
# def Transpose(ordering: ArrayType, array: ArrayType) -> ArrayType:
#     ...


# def _tranpose_sequence(
#     _: CInt, first_order: CInt, ordering: typing.Sequence, array: ArrayType
# ):
#     """
#     Tranpose([first_order, *ordering], array)[first_idx, *idx]
#     == Transpose(new_ordering, array[(<:,> * first_order), first_idx])[idx]

#     Where new_ordering has each value that is above first_order decremented by 1.
#     """
#     first_order_val = first_order.name
#     ordering_val = [o.operands[0].name for o in ordering]
#     new_ordering_val = [o - 1 if o > first_order_val else o for o in ordering_val]

#     first_idx = unbound_content()
#     new_expr = Transpose(
#         vector(*new_ordering_val),
#         OmegaUnary(
#             unary_function(lambda array: Apply(GetItem(array), first_idx)),
#             first_order,
#             array,
#         ),
#     )
#     new_getitem: CGetItem = UnaryFunction(new_expr, first_idx)
#     new_length_expr = array
#     for _1 in range(first_order_val):
#         new_length_expr = Apply(GetItem(new_length_expr), unbound_content())
#     return Sequence(Length(new_length_expr), new_getitem)


# # base case, length 0 vector
# register(
#     Transpose(Sequence(sw("_", Int), VectorCallable()), w("array")),
#     lambda _, array: array,
# )
# # recursive case
# register(
#     Transpose(
#         Sequence(
#             sw("_", Int), VectorCallable(Scalar(sw("first_order", Int)), ws("ordering"))
#         ),
#         w("array"),
#     ),
#     _tranpose_sequence,
#     matchpy.CustomConstraint(
#         lambda ordering: all(
#             isinstance(o, Scalar) and isinstance(o.operands[0], Int)  # type: ignore
#             for o in ordering
#         )
#     ),
# )


# @operation(name="·", to_str=lambda op, l, r: f"({l} ·{op} {r})")
# def OuterProduct(
#     op: CallableBinaryType[ArrayType, ArrayType, ArrayType], l: ArrayType, r: ArrayType
# ) -> ArrayType:
#     ...


# register(
#     OuterProduct(w("op"), Scalar(w("l")), w("r")),
#     lambda op, l, r: BinaryOperation(op, Scalar(l), r),
# )
# register(
#     OuterProduct(w("op"), Sequence(w("length"), w("getitem")), w("r")),
#     lambda op, length, getitem, r: Sequence(
#         length, unary_function(lambda idx: OuterProduct(op, Apply(getitem, idx), r))
#     ),
# )


# @operation(name="·", to_str=lambda l_op, r_op, l, r: f"({l} {l_op}·{r_op} {r})")
# def InnerProduct(l_op, r_op, l: ArrayType, r: ArrayType) -> ArrayType:
#     ...


# # inner product is associative with scalar multiplication
# # TODO: Make this commutative so works for other orders of inner product and binary op.
# register(
#     InnerProduct(
#         Function(Add(ws.add_args), ws.add_args2),
#         Function(Multiply(ws.mult_args), ws.mult_args2),
#         w.l,
#         BinaryOperation(
#             Function(Multiply(ws.inner_mult_args), ws.inner_mult_args2),
#             Scalar(w("s")),
#             w.r,
#         ),
#     ),
#     lambda l, s, r, add_args, add_args2, mult_args, mult_args2, inner_mult_args, inner_mult_args2: BinaryOperation(
#         Function(Multiply(*inner_mult_args), *inner_mult_args),
#         Scalar(s),
#         InnerProduct(
#             Function(Add(*add_args), *add_args),
#             Function(Multiply(*mult_args), mult_args),
#             l,
#             r,
#         ),
#     ),
# )
