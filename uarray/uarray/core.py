import functools
import typing
from .machinery import *
from .core_types import *


@operation
def CallUnary(fn: CCallableUnary[RET, ARG1], a1: ARG1) -> RET:
    ...


@operation
def CallVariadic(fn: CCallableUnary[RET, ARG1], *a1: ARG1) -> RET:
    ...


@operation(to_str=lambda fn, a1, a2: f"{fn}({a1}, {a2})")
def CallBinary(fn: CCallableBinary[RET, ARG1, ARG2], a1: ARG1, a2: ARG2) -> RET:
    ...


@operation
def Sequence(length: CContent, getitem: CGetItem) -> CArray:
    ...


@operation
def GetItem(array: CArray) -> CGetItem:
    ...


# possible other forms:

# @register_
# def _seq_ss(length: CContent, getitem: CGetItem):
#     return lambda: GetItem(Sequence(length, getitem)), lambda: getitem


# with w[CContent] as length, w[CGetItem] as getitem:
#     register(Sequence(length, getitem), getitem)


# @register
# def _getitem_sequence(length: CContent, getitem: CGetItem):
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
def Unbound(*, variable_name: str) -> CUnbound:
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
    return Unbound(variable_name=variable_name or gensym())


def unbound_content(variable_name: str = None) -> CUnboundContent:
    return typing.cast(CUnboundContent, unbound())


def unary_function(fn: typing.Callable[[ARG1], RET]) -> CCallableUnary[RET, ARG1]:
    a1 = unbound()
    return UnaryFunction(fn(typing.cast(ARG1, a1)), a1)


def binary_function(
    fn: typing.Callable[[ARG1, ARG2], RET]
) -> CCallableBinary[RET, ARG1, ARG2]:
    a1 = unbound()
    a2 = unbound()
    return BinaryFunction(fn(typing.cast(ARG1, a1), typing.cast(ARG2, a2)), a1, a2)


@symbol
def Int(name: int) -> CInt:
    pass


@functools.singledispatch
def to_array(v) -> CArray:
    """
    Convert some value into a matchpy expression
    """
    raise NotImplementedError()


@to_array.register(int)
def to_array__int(v):
    return Scalar(Int(v))


@to_array.register(matchpy.Expression)
def to_array__expr(v):
    return v


@operation
def VectorIndexed(idx: CContent, *items: T) -> T:
    ...


register(
    VectorIndexed(sw("index", Int), ws("items")), lambda index, items: items[index.name]
)

CVectorCallable = CCallableUnary[T, CContent]


@operation(to_str=lambda items: f"<{' '.join(str(i) for i in items)}>")
def VectorCallable(*items: T) -> CVectorCallable[T]:
    ...


register(
    CallUnary(VectorCallable(ws("items")), w("index")),
    lambda items, index: VectorIndexed(index, *items),
)


@operation
def PushVectorCallable(
    new_item: T, vector_callable: CVectorCallable[T]
) -> CVectorCallable[T]:
    ...


register(
    PushVectorCallable(w("new_item"), VectorCallable(ws("items"))),
    lambda new_item, items: VectorCallable(new_item, *items),
)


def vector_of(*values: CArray) -> CArray:
    return Sequence(Int(len(values)), VectorCallable(*values))


def vector(*values: typing.Any) -> CArray:
    return vector_of(*map(to_array, values))


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


def with_shape(x: CArray, shape: typing.Sequence[CContent], i=0) -> CArray:
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
    return with_dims(typing.cast(CArray, unbound(variable_name)), n_dim)


def unbound_with_shape(variable_name: str, n_dim: int) -> CArray:
    return with_shape(
        typing.cast(CArray, unbound(variable_name)),
        tuple(unbound_content(f"{variable_name}_shape_{i}") for i in range(n_dim)),
    )
