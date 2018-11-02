import matchpy
import typing

from .machinery import *
from .core import *


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


def _shape(length, getitem):

    inner_shape = Shape(Call(getitem, Unbound()))

    return Sequence(
        Add(Value(1), Length(inner_shape)),
        PushVectorCallable(length, GetItem(inner_shape)),
    )


register(Shape(Scalar(w._)), lambda _: vector())
register(Shape(Sequence(w.length, w.getitem)), _shape)


class Index(matchpy.Operation):
    name = "ψ"
    infix = True
    arity = matchpy.Arity(2, True)


def _index(idx_length, idx_getitem, seq):
    for i in range(idx_length.value):
        index_value = Call(idx_getitem, Value(i))
        seq = Call(GetItem(seq), Content(index_value))
    return seq


register(Index(Sequence(Value.w.idx_length, w.idx_getitem), w.seq), _index)


class ReduceVector(matchpy.Operation):
    """
    ReduceVector(callable, initial_value, sequence)
    """

    name = "red"
    arity = matchpy.Arity(3, True)


def _reduce_vector(value, operation, length, getitem):
    for i in range(length.value):
        value = Call(operation, value, Content(Call(getitem, Value(i))))
    return value


register(
    ReduceVector(w.operation, Value.w.value, Sequence(Value.w.length, w.getitem)),
    _reduce_vector,
)


class Add(matchpy.Operation):
    name = "+"
    infix = True
    arity = matchpy.Arity(2, True)


register(Add(Value.w.l, Value.w.r), lambda l, r: Value(l.value + r.value))


class Multiply(matchpy.Operation):
    name = "*"
    infix = True
    arity = matchpy.Arity(2, True)


register(Multiply(Value.w.l, Value.w.r), lambda l, r: Value(l.value * r.value))


class Pi(matchpy.Operation):
    name = "π"
    arity = matchpy.Arity(1, True)


register(Pi(w.x), lambda x: ReduceVector(function(2, Multiply), Value(1), x))


class Total(matchpy.Operation):
    name = "τ"
    arity = matchpy.Arity(1, True)


register(Total(w.x), lambda x: Pi(Shape(w.x)))


class Iota(matchpy.Operation):
    """
    Iota(n) returns a vector of 0 to n-1.
    """

    name = "ι"
    arity = matchpy.Arity(1, True)


register(Iota(Scalar(w.n)), lambda n: Sequence(n, function(1, Scalar)))


class Dim(matchpy.Operation):
    """
    Dimensionality
    """

    name = "δ"
    arity = matchpy.Arity(1, True)


register(Dim(w.x), lambda x: Pi(Shape(Shape(x))))


# class Args(matchpy.Operation):
#     """
#     Args(x, y)
#     """

#     name = "Args"
#     arity = matchpy.Arity(2, True)


# class ComArgs(matchpy.Operation):
#     """
#     ComArgs(x, y)
#     """

#     name = "ComArgs"
#     arity = matchpy.Arity(2, True)
#     commutative = True


class BinaryOperation(matchpy.Operation):
    """
    BinaryOperation(op, l, r)
    """

    name = "BinaryOperation"
    arity = matchpy.Arity(3, True)


# Both scalars

register(
    BinaryOperation(w.op, Scalar(w.l), Scalar(w.r)),
    lambda op, l, r: Scalar(Call(op, l, r)),
)

# register(
#     BinaryOperation(w.op, Args(Scalar(w.l), Scalar(w.r))),
#     lambda op, l, r: Scalar(Call(op, l, r)),
# )

# One scalar

# register(
#     BinaryOperation(w.op, ComArgs(Scalar(w.s), Sequence(w.length, w.getitem))),
#     lambda op, s, length, getitem: Sequence(
#         length,
#         function(
#             1, lambda idx: BinaryOperation(op, ComArgs(Scalar(s), Call(getitem, idx)))
#         ),
#     ),
# )

register(
    BinaryOperation(w.op, Scalar(w.s), Sequence(w.length, w.getitem)),
    lambda op, s, length, getitem: Sequence(
        length,
        function(1, lambda idx: BinaryOperation(op, Scalar(s), Call(getitem, idx))),
    ),
)
register(
    BinaryOperation(w.op, Sequence(w.length, w.getitem), Scalar(w.s)),
    lambda op, s, length, getitem: Sequence(
        length,
        function(1, lambda idx: BinaryOperation(op, Call(getitem, idx), Scalar(s))),
    ),
)

# neither scalars

# register(
#     BinaryOperation(
#         w.op,
#         ComArgs(Sequence(w.l_length, w.r_getitem), Sequence(w.r_length, w.r_getitem)),
#     ),
#     lambda op, l_length, l_getitem, r_length, r_getitem: Sequence(
#         Unify(l_length, r_length),
#         function(
#             1,
#             lambda idx: BinaryOperation(
#                 op, ComArgs(Call(l_getitem, idx), Call(r_getitem, idx))
#             ),
#         ),
#     ),
# )

register(
    BinaryOperation(
        w.op, Sequence(w.l_length, w.r_getitem), Sequence(w.r_length, w.r_getitem)
    ),
    lambda op, l_length, l_getitem, r_length, r_getitem: Sequence(
        Unify(l_length, r_length),
        function(
            1,
            lambda idx: BinaryOperation(op, Call(l_getitem, idx), Call(r_getitem, idx)),
        ),
    ),
)


class OmegaUnary(matchpy.Operation):
    """
    OmegaUnary(function, dim, array)
    """

    name = "OmegaUnary"
    arity = matchpy.Arity(3, True)


def _omega_unary_sequence(fn, dim, array):
    if dim.value == 0:
        return Call(fn, array)
    new_dim = Value(dim.value - 1)
    return Sequence(
        Length(array),
        function(
            1, lambda idx: _omega_unary_sequence(fn, new_dim, Call(GetItem(array), idx))
        ),
    )


register(OmegaUnary(w.fn, Value.w.dim, w.array), _omega_unary_sequence)


class Transpose(matchpy.Operation):
    """
    Transpose(ordering, array)
    """

    name = "Tranpose"
    arity = matchpy.Arity(2, True)
    infix = True


def _tranpose_sequence(
    _: Value, first_order: Value, ordering: typing.List[Value], array
):
    """
    Tranpose([first_order, *ordering], array)[first_idx, *idx]
    == Transpose(new_ordering, array[(<:,> * first_order), first_idx])[idx]

    Where new_ordering has each value that is above first_order decremented by 1.
    """
    first_order_val = first_order.value
    ordering_val = [o.value for o in ordering]
    new_ordering_val = [o - 1 if o > first_order_val else o for o in ordering_val]

    first_idx = Unbound(gensym())
    new_expr = Transpose(
        vector(*new_ordering_val),
        OmegaUnary(
            function(1, lambda array: Call(GetItem(array), first_idx)),
            first_order,
            array,
        ),
    )
    new_getitem = Function(new_expr, first_idx)
    return Sequence(Length(new_expr), new_getitem)


# base case, length 0 vector
register(
    Transpose(Sequence(Value.w._, VectorCallable()), w.array), lambda _, array: array
)
# recursive case
register(
    Transpose(
        Sequence(Value.w._, VectorCallable(Value.w.first_order, ws.ordering)), w.array
    ),
    matchpy.CustomConstraint(
        lambda ordering: all(isinstance(o, Value) for o in ordering)
    ),
    _tranpose_sequence,
)


class OuterProduct(matchpy.Operation):
    """
    OuterProduct(op, l, r)
    """

    name = "·"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        op, l, r = self.operands
        return f"({l} ·{op} {r})"


register(
    OuterProduct(w.op, Scalar(w.l), w.r),
    lambda op, l, r: BinaryOperation(op, Scalar(l), r),
)
register(
    OuterProduct(w.op, Sequence(w.length, w.getitem), w.r),
    lambda op, length, getitem, r: Sequence(
        length, function(1, lambda idx: OuterProduct(op, Call(getitem, idx), r))
    ),
)


class InnerProduct(matchpy.Operation):
    """
    InnerProduct(l_op, r_op, l, r)
    """

    name = "·"
    arity = matchpy.Arity(4, True)

    def __str__(self):
        op_l, op_r, l, r = self.operands
        return f"({l} {op_l}·{op_r} {r})"


# inner product is associative with scalar multiplication
# TODO: Make this commutative so works for other orders of inner product and binary op.
register(
    InnerProduct(
        Function(Add(ws.add_args), ws.add_args2),
        Function(Multiply(ws.mult_args), ws.mult_args2),
        w.l,
        BinaryOperation(
            Function(Multiply(ws.inner_mult_args), ws.inner_mult_args2),
            Scalar(w.s),
            w.r,
        ),
    ),
    lambda l, s, r, add_args, add_args2, mult_args, mult_args2, inner_mult_args, inner_mult_args2: BinaryOperation(
        Function(Multiply(*inner_mult_args), *inner_mult_args),
        Scalar(s),
        InnerProduct(
            Function(Add(*add_args), *add_args),
            Function(Multiply(*mult_args), mult_args),
            l,
            r,
        ),
    ),
)
