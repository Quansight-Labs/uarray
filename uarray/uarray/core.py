import functools
import typing as t
from .machinery import *


RET = t.TypeVar("RET")
ARG1 = t.TypeVar("ARG1")
ARG2 = t.TypeVar("ARG2")

# Categories

CArray = t.NewType("CArray", object)
CContent = t.NewType("CContent", object)
CUnbound = t.NewType("CUnbound", object)


class CCallableUnary(t.Generic[RET, ARG1]):
    pass


class CCallableBinary(t.Generic[RET, ARG1, ARG2]):
    pass


CGetitem = CCallableUnary[CArray, CContent]

# Functors


@operation
def CallUnary(fn: CCallableUnary[RET, ARG1], a1: ARG1) -> RET:
    ...


@operation(to_str=lambda fn, a1, a2: f"{fn}({a1}, {a2})")
def CallBinary(fn: CCallableBinary[RET, ARG1, ARG2], a1: ARG1, a2: ARG2) -> RET:
    ...


@operation
def Sequence(length: CContent, getitem: CGetitem) -> CArray:
    ...


@operation
def GetItem(array: CArray) -> CGetitem:
    ...


# possible other forms:

# @register_
# def _seq_ss(length: CContent, getitem: CGetitem):
#     return lambda: GetItem(Sequence(length, getitem)), lambda: getitem


# with w[CContent] as length, w[CGetitem] as getitem:
#     register(Sequence(length, getitem), getitem)


# @register
# def _getitem_sequence(length: CContent, getitem: CGetitem):
#     return GetItem(Sequence(length, content)), getitem


register(GetItem(Sequence(w("length"), w("getitem"))), lambda length, getitem: getitem)


@operation
def Length(seq: CArray) -> CContent:
    ...


register(Length(Sequence(w("length"), w("_"))), lambda _, length: length)


@operation
def Scalar(cont: CContent) -> CArray:
    ...


@operation
def Content(sca: CArray) -> CContent:
    ...


register(Content(Scalar(w("content"))), lambda content: content)


@operation
def Unbound(name: str, *, variable_name: str) -> CUnbound:
    ...


# def unbound_content(variable_name: str) -> CContent:
#     return Unbound(name="", variable_name=variable_name)


@operation(to_str=lambda body, a1: f"({a1} -> {body})")
def UnaryFunction(body: RET, a1: CUnbound) -> CCallableUnary[RET, ARG1]:
    ...


@operation(to_str=lambda body, a1, a2: f"({a1}, {a2} -> {body})")
def BinaryFunction(
    body: RET, a1: CUnbound, a2: CUnbound
) -> CCallableBinary[RET, ARG1, ARG2]:
    ...


register(
    CallUnary(UnaryFunction(w("body"), ws("args")), ws("arg_vals")),  # type: ignore
    lambda body, args, arg_vals: matchpy.substitute(
        body, {arg.variable_name: arg_val for (arg, arg_val) in zip(args, arg_vals)}
    ),
)


_counter = 0


def gensym() -> str:
    global _counter
    variable_name = f"i{_counter}"
    _counter += 1
    return variable_name
def unbound(variable_name: str = None) -> CUnbound:


    return Unbound("", variable_name=variable_name or gensym())


def unary_function(fn: t.Callable[[ARG1], RET]) -> CCallableUnary[RET, ARG1]:
    a1 = unbound()
    return UnaryFunction(fn(t.cast(ARG1, a1)), a1)


def binary_function(
    fn: t.Callable[[ARG1, ARG2], RET]
) -> CCallableBinary[RET, ARG1, ARG2]:
    a1 = unbound()
    a2 = unbound()
    return BinaryFunction(fn(t.cast(ARG1, a1), t.cast(ARG2, a2)), a1, a2)


@symbol
def Int(name: int) -> CContent:
    pass


@functools.singledispatch
def to_expression(v) -> matchpy.Expression:
    """
    Convert some value into a matchpy expression
    """
    raise NotImplementedError()


@to_expression.register(int)
def to_expression__int(v):
    return Scalar(Int(v))


@to_expression.register(matchpy.Expression)
def to_expression__expr(v):
    return v


@operation
def VectorIndexed(idx: CContent, *items: T) -> T:
    ...


register(
    VectorIndexed(sw("index", Int), ws("items")),
    lambda index, items: items[index.value],
)

# TODO: Somehow make vector callable both unique and getitem
CVectorCallable = CGetitem


@operation(to_str=lambda items: f"<{' '.join(str(i) for i in items)}>")
def VectorCallable(*items: T) -> CVectorCallable:
    ...


register(
    CallUnary(VectorCallable(ws("items")), w("index")),
    lambda items, index: VectorIndexed(index, *items),
)


@operation
def PushVectorCallable(
    new_item: T, vector_callable: CVectorCallable
) -> CVectorCallable:
    ...


register(
    PushVectorCallable(w("new_item"), VectorCallable(ws("items"))),
    lambda new_item, items: VectorCallable(new_item, *items),
)


def vector_of(*values) -> CArray:
    return Sequence(Int(len(values)), VectorCallable(*values))


def vector(*values) -> CArray:
    return vector_of(*map(to_expression, values))


@operation
def Unify(l: T, r: T) -> T:
    ...

# TODO: Support unification on unequal but equivelent form
# similar to question of equivalencies of lambda calculus, i.e. lambda a: a + 1 == lambda b: b + 1
# even though variables are different name
# Also need to be able to say some thing *could* be equal at runtime, whereas some others cannot be.
# i.e. If two `Value`s are unequal, they cannot be unified. However, if two arbitrary expressions are not equal
# at compile time, they still could end up being equal at runtime.
register(
    Unify(w("x"), w("y")), lambda x, y: x, matchpy.EqualVariablesConstraint("x", "y")
)


def with_shape(x: CArray, shape, i=0) -> CArray:
    if i == len(shape):
        return Scalar(Content(x))
    return Sequence(
        shape[i],
        unary_function(
            lambda idx: with_shape(CallUnary(GetItem(x), idx), shape, i + 1)
        ),
    )


def with_dims(x: CArray, n_dim: int, i=0) -> CArray:
    if i == n_dim:
        return Scalar(Content(x))
    return Sequence(
        Length(x),
        unary_function(lambda idx: with_dims(CallUnary(GetItem(x), idx), n_dim, i + 1)),
    )


def unbound_array(variable_name: str, n_dim: int) -> CArray:
    return with_dims(t.cast(CArray, unbound(variable_name)), n_dim)


def unbound_array_with_shape(variable_name: str, n_dim: int) -> CArray:
    return with_shape(
        t.cast(CArray, unbound(variable_name)),
        tuple(unbound(f"{variable_name}_shape_{i}") for i in range(n_dim)),
    )
