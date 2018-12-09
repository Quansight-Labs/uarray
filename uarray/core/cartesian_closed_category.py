from .cartesian_category import *


@operation(name="curry")
def Curry(f: FunctionType[PairType[T, V], U]) -> FunctionType[T, FunctionType[V, U]]:
    ...


@replacement
def _apply_curry(f: FunctionType[PairType[T, V], U], x: T, y: V) -> DoubleThunkType[U]:
    return lambda: Apply(Apply(Curry(f), x), y), lambda: Apply(f, Pair(x, y))


@operation(name="uncurry")
def Uncurry(f: FunctionType[T, FunctionType[V, U]]) -> FunctionType[PairType[T, V], U]:
    ...


@replacement
def _apply_uncurry(
    f: FunctionType[T, FunctionType[V, U]], x: T, y: V
) -> DoubleThunkType[U]:
    return lambda: Apply(Uncurry(f), Pair(x, y)), lambda: Apply(Apply(f, x), y)
