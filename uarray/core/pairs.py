from ..machinery import *
import typing

__all__ = ["Pair", "PairType", "Exl", "Exr"]
T = typing.TypeVar("T")
U = typing.TypeVar("U")


##
# Types
##


class PairType(typing.Generic[T, U]):

    pass


##
# Constructors
##


@operation
def Pair(l: T, r: U) -> PairType[T, U]:
    ...


##
# Operations
##


@operation
def Exl(p: PairType[T, U]) -> T:
    ...


@replacement
def _replace_exl(l: T, r: U) -> DoubleThunkType[T]:
    return lambda: Exl(Pair(l, r)), lambda: l


@operation
def Exr(p: PairType[T, U]) -> U:
    ...


@replacement
def _replace_exr(l: T, r: U) -> DoubleThunkType[U]:
    return lambda: Exr(Pair(l, r)), lambda: r
