import typing

import matchpy

from .core import *


@operation(name="ρ")
def Shape(a: CArray) -> CArray:
    ...


def _shape(length: CContent, getitem: CGetItem):

    inner_shape = Shape(CallUnary(getitem, unbound_content()))

    return Sequence(
        Add(Int(1), Length(inner_shape)),
        PushVectorCallable(Scalar(length), GetItem(inner_shape)),
    )


register(Shape(Scalar(w("_"))), lambda _: vector())
register(Shape(Sequence(w("length"), w("getitem"))), _shape)


# if the index is unbound we should still be able to get shape
# TODO: this is probably bad, then we have two ways of getting vector shape
register(
    Shape(VectorIndexed(w("idx"), ws("xs"))), lambda idx, xs: Unify(*map(Shape, xs))
)


@operation(name="ψ", infix=True)
def Index(indices: CArray, ar: CArray) -> CArray:
    ...


def _index(idx_length, idx_getitem, seq):
    for i in range(idx_length.name):
        index_value = CallUnary(idx_getitem, Int(i))
        seq = CallUnary(GetItem(seq), Content(index_value))
    return seq


register(Index(Sequence(sw("idx_length", Int), w("idx_getitem")), w("seq")), _index)


@operation(name="red")
def ReduceVector(
    fn: CCallableBinary[CArray, CArray, CArray], initial_value: CArray, vec: CArray
) -> CArray:
    ...


def _reduce_vector(fn, value, length, getitem):
    for i in range(length.name):
        value = CallBinary(fn, value, CallUnary(getitem, Int(i)))
    return value


register(
    ReduceVector(w("fn"), w("value"), Sequence(sw("length", Int), w("getitem"))),
    _reduce_vector,
)


@operation(name="+", infix=True)
def Add(l: CContent, r: CContent) -> CContent:
    ...


register(Add(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name + r.name))


@operation(name="*", infix=True)
def Multiply(l: CContent, r: CContent) -> CContent:
    ...


register(Multiply(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name * r.name))


def wrap_binary(
    fn: typing.Callable[[CContent, CContent], CContent]
) -> typing.Callable[[CArray, CArray], CArray]:
    return lambda a, b: Scalar(fn(Content(a), Content(b)))


@operation(name="π")
def Pi(ar: CArray) -> CArray:
    ...


def _pi(ar: CArray) -> CArray:
    return ReduceVector(binary_function(wrap_binary(Multiply)), Scalar(Int(1)), ar)


register(Pi(w("ar")), _pi)


@operation(name="τ")
def Total(ar: CArray) -> CArray:
    ...


register(Total(w("x")), lambda x: Pi(Shape(x)))


@operation(name="ι")
def Iota(n: CArray) -> CArray:
    """
    Iota(n) returns a vector of 0 to n-1.
    """
    ...


register(Iota(Scalar(w("n"))), lambda n: Sequence(n, unary_function(Scalar)))


@operation(name="δ")
def Dim(n: CArray) -> CArray:
    ...


register(Dim(w("x")), lambda x: Pi(Shape(Shape(x))))


@operation(name="%")
def Remainder(l: CContent, r: CContent) -> CContent:
    ...


register(Remainder(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name % r.name))


@operation(name="//")
def Quotient(l: CContent, r: CContent) -> CContent:
    ...


register(Quotient(sw("l", Int), sw("r", Int)), lambda l, r: Int(l.name // r.name))


@operation(name="rav")
def Ravel(n: CArray) -> CArray:
    ...


register(Ravel(Scalar(w("c"))), lambda c: Sequence(Int(1), Always(Scalar(c))))


def _ravel_sequence(length: CContent, getitem: CGetItem) -> CArray:
    a = Sequence(length, getitem)

    inner_size = Content(Total(CallUnary(getitem, unbound_content())))

    def new_getitem(idx: CContent) -> CArray:
        this_idx = Quotient(idx, inner_size)
        next_idx = Remainder(idx, inner_size)
        return CallUnary(GetItem(Ravel(CallUnary(getitem, this_idx))), next_idx)

    return Sequence(Content(Total(a)), unary_function(new_getitem))


register(Ravel(Sequence(w("length"), w("getitem"))), _ravel_sequence)


@operation(name="ρvec")
def ReshapeVector(new_shape: CVectorCallable, vec: CArray) -> CArray:
    ...


def _reshape_vector_scalar(length: CContent, getitem: CGetItem) -> CArray:
    return Scalar(Content(CallUnary(getitem, Int(0))))


register(
    ReshapeVector(VectorCallable(), Sequence(w("length"), w("getitem"))),
    _reshape_vector_scalar,
)


def _reshape_vector_array(
    new_length: CContent,
    rest: typing.Iterable[CArray],
    length: CContent,
    getitem: CGetItem,
) -> CArray:
    inner_size = Content(Pi(vector_of(*rest)))

    def new_getitem(idx: CContent) -> CArray:
        offset = Multiply(inner_size, idx)

        def inner_getitem(inner_idx: CContent) -> CArray:
            return CallUnary(getitem, Remainder(Add(inner_idx, offset), length))

        return ReshapeVector(
            VectorCallable(*rest), Sequence(inner_size, unary_function(inner_getitem))
        )

    return Sequence(new_length, unary_function(new_getitem))


register(
    ReshapeVector(
        VectorCallable(Scalar(w("new_length")), ws("rest")),
        Sequence(w("length"), w("getitem")),
    ),
    _reshape_vector_array,
)


@operation(name="ρ")
def Reshape(new_shape: CArray, array: CArray, array_dim: CArray) -> CArray:
    """
    Reshape command that is sufficient for NP broadcasting. Doesn't support full reshape semantics yet.

    input array should be broadcastable into result array
    """
    ...


# def _reshape(
#     new_shape_length: CInt,
#     new_shape_contents: typing.Sequence[CArray],
#     array_length: CInt,
#     array_getitem: CGetItem,
#     array_dim: CInt,
# ) -> CArray:
#     if array_dim.name > new_shape_length.name:
#         raise NotImplementedError("Only support reshaping to dims >= original")
#     new_length, *rest = new_shape_contents
#     if array_dim.name < new_shape_length.name:
#         # if we are reshaping to more dimensions, then we wanna just
#         # set this length and recurse down

#         def new_getitem(idx: CContent) -> CArray:
#             return Reshape(
#                 vector_of(*rest),
#                 Sequence(Content(new_length), array_getitem),
#                 Scalar(array_dim),
#             )
#         return Sequence(Content(new_length), unary_function(new_getitem))
#     # otherwise we have equal dimensions
#     if array_length == new_shape_length
#     if new_shape_length == array_dim:
#         new_length, *rest = new_shape_contents

#         def new_getitem(idx: CContent) -> CArray:
#             GetItem(array)

#         return Sequence(Content(new_length), unary_function(new_getitem))
#     #     return UpdateWithLength(array, new_shape[0])
#     #     recurss
#     # else:


# register(
#     Reshape(
#         Sequence(sw("new_shape_length", Int), VectorCallable(w(), ws("new_shape_contents"))),
#         Sequence(sw("array_length", Int), w("array_getitem")),
#         Scalar(sw("array_dim", Int)),
#     ),
#     _reshape,
# )


@operation
def BinaryOperation(
    op: CCallableBinary[CArray, CArray, CArray], l: CArray, r: CArray
) -> CArray:
    ...


# Both scalars

register(
    BinaryOperation(w("op"), Scalar(w("l")), Scalar(w("r"))),
    lambda op, l, r: CallBinary(op, Scalar(l), Scalar(r)),
)


register(
    BinaryOperation(w("op"), Scalar(w("s")), Sequence(w("length"), w("getitem"))),
    lambda op, s, length, getitem: Sequence(
        length,
        unary_function(
            lambda idx: BinaryOperation(op, Scalar(s), CallUnary(getitem, idx))
        ),
    ),
)
register(
    BinaryOperation(w("op"), Sequence(w("length"), w("getitem")), Scalar(w("s"))),
    lambda op, s, length, getitem: Sequence(
        length,
        unary_function(
            lambda idx: BinaryOperation(op, CallUnary(getitem, idx), Scalar(s))
        ),
    ),
)


register(
    BinaryOperation(
        w("op"),
        Sequence(w("l_length"), w("l_getitem")),
        Sequence(w("r_length"), w("r_getitem")),
    ),
    lambda op, l_length, l_getitem, r_length, r_getitem: Sequence(
        Unify(l_length, r_length),
        unary_function(
            lambda idx: BinaryOperation(
                op, CallUnary(l_getitem, idx), CallUnary(r_getitem, idx)
            )
        ),
    ),
)


@operation
def OmegaUnary(
    function: CCallableUnary[CArray, CArray], dim: CContent, array: CArray
) -> CArray:
    ...


# TODO: Make this invese. if 0 we should keep traversing
def _omega_unary_sequence(
    fn: CCallableUnary[CArray, CArray], dim: CInt, array: CArray
) -> CArray:
    if dim.name == 0:
        return CallUnary(fn, array)
    new_dim = Int(dim.name - 1)
    return Sequence(
        Length(array),
        unary_function(
            lambda idx: _omega_unary_sequence(
                fn, new_dim, CallUnary(GetItem(array), idx)
            )
        ),
    )


register(OmegaUnary(w("fn"), sw("dim", Int), w("array")), _omega_unary_sequence)


@operation(infix=True)
def Transpose(ordering: CArray, array: CArray) -> CArray:
    ...


def _tranpose_sequence(
    _: CInt, first_order: CInt, ordering: typing.Sequence, array: CArray
):
    """
    Tranpose([first_order, *ordering], array)[first_idx, *idx]
    == Transpose(new_ordering, array[(<:,> * first_order), first_idx])[idx]

    Where new_ordering has each value that is above first_order decremented by 1.
    """
    first_order_val = first_order.name
    ordering_val = [o.operands[0].name for o in ordering]
    new_ordering_val = [o - 1 if o > first_order_val else o for o in ordering_val]

    first_idx = unbound_content()
    new_expr = Transpose(
        vector(*new_ordering_val),
        OmegaUnary(
            unary_function(lambda array: CallUnary(GetItem(array), first_idx)),
            first_order,
            array,
        ),
    )
    new_getitem: CGetItem = UnaryFunction(new_expr, first_idx)
    new_length_expr = array
    for _1 in range(first_order_val):
        new_length_expr = CallUnary(GetItem(new_length_expr), unbound_content())
    return Sequence(Length(new_length_expr), new_getitem)


# base case, length 0 vector
register(
    Transpose(Sequence(sw("_", Int), VectorCallable()), w("array")),
    lambda _, array: array,
)
# recursive case
register(
    Transpose(
        Sequence(
            sw("_", Int), VectorCallable(Scalar(sw("first_order", Int)), ws("ordering"))
        ),
        w("array"),
    ),
    _tranpose_sequence,
    matchpy.CustomConstraint(
        lambda ordering: all(
            isinstance(o, Scalar) and isinstance(o.operands[0], Int)  # type: ignore
            for o in ordering
        )
    ),
)


@operation(name="·", to_str=lambda op, l, r: f"({l} ·{op} {r})")
def OuterProduct(
    op: CCallableBinary[CArray, CArray, CArray], l: CArray, r: CArray
) -> CArray:
    ...


register(
    OuterProduct(w("op"), Scalar(w("l")), w("r")),
    lambda op, l, r: BinaryOperation(op, Scalar(l), r),
)
register(
    OuterProduct(w("op"), Sequence(w("length"), w("getitem")), w("r")),
    lambda op, length, getitem, r: Sequence(
        length, unary_function(lambda idx: OuterProduct(op, CallUnary(getitem, idx), r))
    ),
)


@operation(name="·", to_str=lambda l_op, r_op, l, r: f"({l} {l_op}·{r_op} {r})")
def InnerProduct(l_op, r_op, l: CArray, r: CArray) -> CArray:
    ...


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
