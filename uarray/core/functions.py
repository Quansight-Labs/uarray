from .cartesian_closed_category import *


def Const(x: T) -> FunctionType[typing.Any, T]:
    """
    Function that always returns x
    """
    ...


@replacement
def _apply_const(x: T, arg: typing.Any) -> DoubleThunkType[T]:
    return (lambda: Apply(Const(x), arg), lambda: x)


class Function(Symbol[typing.Callable[[T], U]], FunctionType[T, U]):
    pass


@replacement
def _call_function(fn: Function[T, U], arg: T) -> DoubleThunkType[U]:
    return (lambda: Apply(fn, arg), lambda: fn.value()(arg))


class BinaryFunction(
    Symbol[typing.Callable[[T, U], V]], FunctionType[T, FunctionType[U, V]]
):
    pass


@replacement
def _call_binary_function(
    fn: BinaryFunction[T, U, V], arg1: T, arg2: U
) -> DoubleThunkType[V]:
    return (lambda: Apply(Apply(fn, arg1), arg2), lambda: fn.value()(arg1, arg2))


class TernaryFunction(
    Symbol[typing.Callable[[T, U, V], R]],
    FunctionType[T, FunctionType[U, FunctionType[V, R]]],
):
    pass


@replacement
def _call_ternary_function(
    fn: TernaryFunction[T, U, V, R], arg1: T, arg2: U, arg3: V
) -> DoubleThunkType[R]:
    return (
        lambda: Apply(Apply(Apply(fn, arg1), arg2), arg3),
        lambda: fn.value()(arg1, arg2, arg3),
    )
