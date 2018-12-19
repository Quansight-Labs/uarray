import typing

from ..machinery import *
from .booleans import *

T = typing.TypeVar("T")

__all__ = ["Unify", "Equal"]


##
# Operations
##


@operation
def Unify(*args: T) -> T:
    """
    Asserts all args are equal to the same value and returns it.
    """
    ...


@replacement
def _unify_single(x: T) -> DoubleThunkType[T]:
    return lambda: Unify(x), lambda: x


@replacement
def _unify_multiple(x: T, xs: typing.Sequence[T]) -> DoubleThunkType[T]:
    return lambda: Unify(x, x, *xs), lambda: Unify(x, *xs)


@operation
def Equal(x: T, y: T) -> BoolType:
    ...


@replacement
def _equal_same_vars(x: T) -> DoubleThunkType[BoolType]:
    return lambda: Equal(x, x), lambda: bool_(True)
