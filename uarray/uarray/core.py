# pylint: disable=E1120,W0108,W0621,E1121,E1101
import matchpy
import typing
import functools
from .machinery import *

__all__ = [
    "Sequence",
    "Call",
    "Value",
    "scalar",
    "vector",
    "vector_of",
    "Unbound",
    "Scalar",
    "Content",
    "GetItem",
    "Function",
    "function",
    "Length",
    "to_expression",
    "PushVectorCallable",
    "with_dims",
    "Unify",
    "unbound",
    "VectorIndexed",
    "gensym",
    "with_shape",
]


class Sequence(matchpy.Operation):
    """
    Sequence(length, getitem)
    """

    name = "Sequence"
    arity = matchpy.Arity(2, True)


class GetItem(matchpy.Operation):
    name = "GetItem"
    arity = matchpy.Arity(1, True)


register(GetItem(Sequence(w._, w.getitem)), lambda _, getitem: getitem)


class Length(matchpy.Operation):
    name = "Length"
    arity = matchpy.Arity(1, True)


register(Length(Sequence(w.length, w._)), lambda _, length: length)


class Scalar(matchpy.Operation):
    """
    Scalar(content)
    """

    name = "Scalar"
    arity = matchpy.Arity(1, True)

    def __str__(self):
        return str(self.operands[0])


class Content(matchpy.Operation):
    name = "Content"
    arity = matchpy.Arity(1, True)


register(Content(Scalar(w.content)), lambda content: content)


class Call(matchpy.Operation):
    """
    Call(callable, *args)
    """

    name = "Call"
    arity = matchpy.Arity(1, False)

    def __str__(self):
        callable, *args = self.operands
        return f"{callable}({', '.join(map(str, args))})"


class Function(matchpy.Operation):
    """
    Function(body, *args)
    """

    name = "Function"
    arity = matchpy.Arity(1, False)

    def __str__(self):
        body, *args = self.operands
        return f"({', '.join(a.variable_name for a in args)} -> {body})"


register(
    Call(Function(w.body, ws.args), ws.arg_vals),
    lambda body, args, arg_vals: matchpy.substitute(
        body, {arg.variable_name: arg_val for (arg, arg_val) in zip(args, arg_vals)}
    ),
)

_counter = 0


def gensym():
    global _counter
    variable_name = f"i{_counter}"
    _counter += 1
    return variable_name


def function(n, fn):
    """
    function(n, lambda arg_1, arg_2, ..., arg_n: body)
    """
    args = [Unbound(gensym()) for _ in range(n)]
    return Function(fn(*args), *args)


class Value(matchpy.Symbol):
    def __init__(self, value):
        self.value = value
        super().__init__(repr(value), None)

    def __str__(self):
        return str(self.value)


def scalar(value):
    return Scalar(Value(value))


@functools.singledispatch
def to_expression(v) -> matchpy.Expression:
    """
    Convert some value into a matchpy expression
    """
    return scalar(v)


@to_expression.register(matchpy.Expression)
def to_expression__expr(v):
    return v


class VectorCallable(matchpy.Operation):
    """
    VectorCallable(*items)
    """

    name = "VectorCallable"
    arity = matchpy.Arity(0, False)

    def __str__(self):
        return f"<{' '.join(map(str, self.operands))}>"


register(
    Call(VectorCallable(ws.items), w.index),
    lambda items, index: Scalar(VectorIndexed(index, *items)),
)


class PushVectorCallable(matchpy.Operation):
    """
    PushVectorCallable(new_item, VectorCallable())
    """

    name = "PushVectorCallable"
    arity = matchpy.Arity(2, True)

    def __str__(self):
        return f"<{self.operands[0]}, *{self.operands[1]}>"


register(
    PushVectorCallable(w.new_item, VectorCallable(ws.items)),
    lambda new_item, items: VectorCallable(new_item, *items),
)


class VectorIndexed(matchpy.Operation):
    """
    VectorIndexed(index, *items)
    """

    name = "VectorIndexed"
    arity = matchpy.Arity(1, False)


register(
    VectorIndexed(Value.w.index, ws.items), lambda index, items: items[index.value]
)


def vector_of(*values):
    return Sequence(Value(len(values)), VectorCallable(*values))


def vector(*values):
    return vector_of(*(Value(v) for v in values))


class Unbound(matchpy.Symbol):
    def __init__(self, variable_name=None):
        super().__init__(name="", variable_name=variable_name)

    def __str__(self):
        return self.variable_name or "_"


# class If(matchpy.Operation):
#     name = "If"
#     arity = matchpy.Arity(3, True)


# register(
#     If(Value.w.cond, w.true, w.false),
#     lambda cond, true, false: true if cond.value else false,
# )


# class IsZero(matchpy.Operation):
#     name = "IsZero"
#     arity = matchpy.Arity(1, True)


# register(IsZero(Value.w.x), lambda x: x.value == 0)


class Unify(matchpy.Operation):
    """
    Unify(x, y) asserts x and y are equivalen and returns them
    """

    name = "Unify"
    arity = matchpy.Arity(2, True)


register(Unify(w.x, w.y), matchpy.EqualVariablesConstraint("x", "y"), lambda x, y: x)


def with_shape(
    x: matchpy.Expression, shape: typing.Tuple[matchpy.Expression, ...], i=0
):
    if i == len(shape):
        return Scalar(Content(x))
    return Sequence(
        shape[i],
        function(1, lambda idx: with_shape(Call(GetItem(x), idx), shape, i + 1)),
    )


def with_dims(x: matchpy.Expression, n_dim: int, i=0):
    if i == n_dim:
        return Scalar(Content(x))
    return Sequence(
        Length(x),
        function(1, lambda idx: with_dims(Call(GetItem(x), idx), n_dim, i + 1)),
    )


def unbound(variable_name, n_dim):
    return with_dims(Unbound(variable_name), n_dim)
