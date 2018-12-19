import typing

from ..machinery import *

T = typing.TypeVar("T")

__all__ = ["BoolType", "bool_", "symbols_equal", "If"]


##
# Types
##


class BoolType:
    """
    Boolean
    """

    pass


##
# Constructors
##


@operation
def TrueBool() -> BoolType:
    ...


@operation
def FalseBool() -> BoolType:
    ...


##
# Helper constructors
##


def bool_(x: bool) -> BoolType:
    if x:
        return TrueBool()
    return FalseBool()


def symbols_equal(x: Symbol[T], y: Symbol[T]) -> BoolType:
    return bool_(x.value() == y.value())


##
# Operations
##


@operation
def If(cond: BoolType, is_true: T, is_false: T) -> T:
    """
    if cond:
        return is_zero
    return isnt_zero
    """
    ...


@replacement
def _if_is_true(is_true: T, is_false: T) -> DoubleThunkType[T]:
    return lambda: If(TrueBool(), is_true, is_false), lambda: is_true


@replacement
def _if_is_false(is_true: T, is_false: T) -> DoubleThunkType[T]:
    return lambda: If(FalseBool(), is_true, is_false), lambda: is_false
