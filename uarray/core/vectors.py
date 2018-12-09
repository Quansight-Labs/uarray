from .lists import *


# length and content
VecType = PairType[NatType, ListType[T_COV]]


@operation
def ListToVec(l: ListType[T]) -> VecType[T]:
    """
    Wraps a list into a vector
    """
    ...


@replacement
def _list_to_vec(l: T) -> DoubleThunkType[VecType[T]]:
    return lambda: ListToVec(List(*xs)), lambda: Pair(Int(len(xs)), List(*xs))


@operation
def VecFirst(v: VecType[T]) -> T:
    ...


@replacement
def _vec_first(length: NatType, x: T, xs: typing.Sequence[T]) -> DoubleThunkType[T]:
    return (lambda: VecFirst(Pair(length, List(x, *xs))), lambda: x)


@operation
def VecRest(v: VecType[T]) -> VecType[T]:
    ...


@replacement
def _vec_rest(length: Int, x: T, xs: typing.Sequence[T]) -> DoubleThunkType[VecType[T]]:
    return (
        lambda: VecRest(Pair(length, List(x, *xs))),
        lambda: Pair(Int(length.value() - 1), List(*xs)),
    )


@operation
def VecPush(x: T, v: VecType[T]) -> VecType[T]:
    ...


@replacement
def _vec_push(x: T, length: Int, xs: typing.Sequence[T]) -> DoubleThunkType[VecType[T]]:
    return (
        lambda: VecPush(x, Pair(length, List(*xs))),
        lambda: Pair(Int(length.value() + 1), List(x, *xs)),
    )


@operation
def VecConcat(l: VecType[T], r: VecType[T]) -> VecType[T]:
    ...


@replacement
def _vec_concat(
    l_length: Int, l_xs: typing.Sequence[T], r_length: Int, r_xs: typing.Sequence[T]
) -> DoubleThunkType[VecType[T]]:
    return (
        lambda: VecConcat(Pair(l_length, List(*l_xs)), Pair(r_length, List(*r_xs))),
        lambda: Pair(Int(l_length.value() + r_length.value()), List(*l_xs, *r_xs)),
    )


@operation
def VecDrop(n: NatType, vec: VecType[T]) -> VecType[T]:
    ...


@replacement
def _vec_drop(
    n: Int, length: Int, xs: typing.Sequence[T]
) -> DoubleThunkType[VecType[T]]:
    return (
        lambda: VecDrop(n, Pair(length, List(*xs))),
        lambda: Pair(Int(length.value() - n.value()), List(*xs[n.value() :])),
    )
