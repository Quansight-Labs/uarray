from .arrays import *


@operation
def Unify(*args: T) -> T:
    ...


@replacement
def _unify_single(x: T) -> DoubleThunkType[T]:
    return lambda: Unify(x), lambda: x


@replacement
def _unify_multiple(x: T, xs: typing.Sequence[T]) -> DoubleThunkType[T]:
    return lambda: Unify(x, x, *xs), lambda: Unify(x, *xs)
