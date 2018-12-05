import functools
import typing

from .core_types import *
from .machinery import *


class Int(Symbol[int], NatType):
    pass


@operation
def CallUnary(fn: CallableUnaryType[RET, ARG1], a1: ARG1) -> RET:
    ...


@operation(to_str=lambda fn, a1, a2: f"{fn}({a1}, {a2})")
def CallBinary(fn: CallableBinaryType[RET, ARG1, ARG2], a1: ARG1, a2: ARG2) -> RET:
    ...


# @operation
# def BoundedNat(bound: NatType, value: NatType) -> BoundedNatType:
#     ...


# @operation
# def BoundedNatBound(bnat: BoundedNatType) -> NatType:
#     ...


# @replacement
# def _bound_of_bounded_nat(bound: NatType, value: NatType) -> Pair[NatType]:
#     return (lambda: BoundedNatBound(BoundedNat(bound, value)), lambda: bound)


# @operation
# def BoundedNatValue(bnat: BoundedNatType) -> NatType:
#     ...


# @replacement
# def _bound_of_bounded_value(bound: NatType, value: NatType) -> Pair[NatType]:
#     return (lambda: BoundedNatValue(BoundedNat(bound, value)), lambda: value)


@operation
def Vector(length: NatType, index: ListType[T]) -> VectorType[T]:
    ...


@operation
def VectorIndex(vector: VectorType[T]) -> ListType[T]:
    ...


@replacement
def _index_of_vector(length: NatType, index: ListType[T]) -> Pair[ListType[T]]:
    return (lambda: VectorIndex(Vector(length, index)), lambda: index)


@operation
def VectorLength(vector: VectorType[T]) -> NatType:
    ...


@replacement
def _length_of_vector(length: NatType, index: ListType[T]) -> Pair[NatType]:
    return (lambda: VectorLength(Vector(length, index)), lambda: length)


@operation
def Array(shape: ShapeType, index: ArrayIndexType[T]) -> ArrayType[T]:
    ...


@operation
def ArrayShape(array: ArrayType[T]) -> ShapeType:
    ...


@replacement
def _shape_of_array(shape: ShapeType, index: ArrayIndexType[T]) -> Pair[ShapeType]:
    return (lambda: ArrayShape(Array(shape, index)), lambda: shape)


@operation
def ArrayIndex(array: ArrayType[T]) -> ArrayIndexType[T]:
    ...


@replacement
def _index_of_array(
    shape: ShapeType, index: ArrayIndexType[T]
) -> Pair[ArrayIndexType[T]]:
    return (lambda: ArrayIndex(Array(shape, index)), lambda: index)


@operation(to_str=lambda val: f"_ -> {val}")
def Always(val: T) -> CallableUnaryType[T, typing.Any]:
    ...


@replacement
def _call_always(val: T, arg: typing.Any) -> Pair[T]:
    return (lambda: CallUnary(Always(val), arg), lambda: arg)


@operation
def Compose(
    l: CallableUnaryType[T, V], r: CallableUnaryType[V, U]
) -> CallableUnaryType[T, U]:
    ...


@replacement
def _call_compose(
    l: CallableUnaryType[T, V], r: CallableUnaryType[V, U], v: U
) -> Pair[T]:
    return (lambda: CallUnary(Compose(l, r), v), lambda: CallUnary(l, CallUnary(r, v)))


class PythonUnaryFunction(
    Symbol[typing.Callable[[ARG1], RET]], CallableUnaryType[RET, ARG1]
):
    pass


@replacement
def _call_python_unary_function(
    python_fn: PythonUnaryFunction[ARG1, RET], arg: ARG1
) -> Pair[RET]:
    return (lambda: CallUnary(python_fn, arg), lambda: python_fn.value()(arg))


@functools.singledispatch
def to_array(v) -> ArrayType:
    """
    Convert some value into a matchpy expression
    """
    raise NotImplementedError()


@to_array.register(matchpy.Expression)
def to_array__expr(v):
    return v


# @to_array.register(tuple)
# def to_array__tuple(t):
#     return vector_of(*(to_array(t_) for t_ in t))


@operation(to_str=lambda items: f"<{' '.join(str(i) for i in items)}>")
def List(*items: T) -> ListType[T]:
    ...


@replacement
def _index_list(items: typing.Sequence[T], index: Int) -> Pair[T]:
    return (lambda: CallUnary(List(*items), index), lambda: items[index.value()])


@operation
def Zero() -> NatType:
    ...


@replacement
def _zero() -> Pair[NatType]:
    return lambda: Zero(), lambda: Int(0)


@operation
def ListFirst(vec: ListType[T]) -> T:
    ...


@replacement
def _list_first(l: ListType[T]) -> Pair[T]:
    return (lambda: ListFirst(l), lambda: CallUnary(l, Zero()))


@operation
def ListPush(new_item: T, vec: ListType[T]) -> ListType[T]:
    ...


@replacement
def _list_push(new_item: T, items: typing.Sequence[T]) -> Pair[ListType[T]]:
    return (lambda: ListPush(new_item, List(*items)), lambda: List(new_item, *items))


@operation
def ListConcat(l: ListType[T], r: ListType[T]) -> ListType[T]:
    ...


@replacement
def _list_concat(
    l_items: typing.Sequence[T], r_items: typing.Sequence[T]
) -> Pair[ListType[T]]:
    return (
        lambda: ListConcat(List(*l_items), List(*r_items)),
        lambda: List(*l_items, *r_items),
    )


@operation
def VectorToArray(vec: VectorType) -> ArrayType[T]:
    ...


# vector_first_boxed: typing.Callable[[VectorType[T]], T] = Box(VectorFirst)

first_index: CallableUnaryType[
    NatType, CallableUnaryType[NatType, NatType]
] = PythonUnaryFunction(ListFirst)


@replacement
def _vec_to_array(length: NatType, vec: ListType[T]) -> Pair[ArrayType[T]]:

    return (
        lambda: VectorToArray(Vector(length, vec)),
        lambda: Array(Vector(Int(1), List(length)), Compose(vec, first_index)),
    )


@operation
def Unify(*args: T) -> T:
    ...


# TODO: Support unification on unequal but equivelent form
# similar to question of equivalencies of lambda calculus, i.e. lambda a: a + 1 == lambda b: b + 1
# even though variables are different name
# Also need to be able to say some thing *could* be equal at runtime, whereas some others cannot be.
# i.e. If two `Value`s are unequal, they cannot be unified. However, if two arbitrary expressions are not equal
# at compile time, they still could end up being equal at runtime.
@replacement
def _unify_single(x: T) -> Pair[T]:
    return lambda: Unify(x), lambda: x


@replacement
def _unify_multiple(x: T, xs: typing.Sequence[T]) -> Pair[T]:
    return lambda: Unify(x, x, *xs), lambda: Unify(x, *xs)
