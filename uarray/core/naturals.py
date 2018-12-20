import typing

import matchpy

from ..machinery import *
from .booleans import *
from .equality import *
from .pairs import *
from .abstractions import *

__all__ = [
    "NatType",
    "nat",
    "NatLTE",
    "NatLT",
    "NatIncr",
    "NatMultiply",
    "NatDecr",
    "NatAdd",
    "NatSubtract",
    "NonZeroInt",
    "NatLoop",
]

T = typing.TypeVar("T")
##
# Types
##


class NatType:
    """
    Natural number
    """

    pass


##
# Constructors
##
class Int(Symbol[int], NatType):
    """
    Natural number represented by python integer
    """

    pass


class NonZeroInt(Int):
    """
    Used in replacement so a custom constraint is added
    """

    pass


NonZeroInt.constraint = matchpy.CustomConstraint(  # type: ignore
    lambda i: i.value() != 0
)


##
# Helper constructors
##
def nat(i: int) -> NatType:
    return Int(i)


##
# Operations
##


@replacement
def _are_ints_equal(x: Int, y: Int):
    return lambda: Equal(x, y), lambda: symbols_equal(x, y)


@operation
def NatLTE(l: NatType, r: NatType) -> BoolType:
    """
    l <= r
    """
    ...


@replacement
def _ints_lte(x: Int, y: Int):
    return lambda: NatLTE(x, y), lambda: bool_(x.value() <= y.value())


@operation
def NatLT(l: NatType, r: NatType) -> BoolType:
    """
    l < r
    """
    ...


@replacement
def _ints_lt(x: Int, y: Int):
    return lambda: NatLT(x, y), lambda: bool_(x.value() < y.value())


@operation
def NatIncr(n: NatType) -> NatType:
    ...


@replacement
def _nat_incr(n: Int) -> DoubleThunkType[NatType]:
    return lambda: NatIncr(n), lambda: Int(n.value() + 1)


@operation
def NatDecr(n: NatType) -> NatType:
    ...


@replacement
def _nat_decr(n: Int) -> DoubleThunkType[NatType]:
    return lambda: NatDecr(n), lambda: Int(n.value() - 1)


@operation
def NatAdd(l: NatType, r: NatType) -> NatType:
    ...


@replacement
def _nat_add(l: Int, r: Int) -> DoubleThunkType[NatType]:
    return lambda: NatAdd(l, r), lambda: Int(l.value() + r.value())


@replacement
def _nat_add_0_l(x: NatType):
    return lambda: NatAdd(nat(0), x), lambda: x


@replacement
def _nat_add_0_r(x: NatType):
    return lambda: NatAdd(x, nat(0)), lambda: x


@operation
def NatMultiply(l: NatType, r: NatType) -> NatType:
    ...


@replacement
def _nat_multiply(l: Int, r: Int) -> DoubleThunkType[NatType]:
    return lambda: NatMultiply(l, r), lambda: Int(l.value() * r.value())


@replacement
def _nat_multiply_0_l(x: NatType):
    return lambda: NatMultiply(nat(0), x), lambda: nat(0)


@replacement
def _nat_multiply_0_r(x: NatType):
    return lambda: NatMultiply(x, nat(0)), lambda: nat(0)


@operation
def NatSubtract(l: NatType, r: NatType) -> NatType:
    ...


@replacement
def _nat_subtract(l: Int, r: Int) -> DoubleThunkType[NatType]:
    return lambda: NatSubtract(l, r), lambda: Int(l.value() - r.value())


@operation
def NatLoop(
    initial: T, n: NatType, abstraction: PairType[PairType[NatType, T], T]
) -> T:
    """
    v = initial
    for i in range(n):
        v = abstraction(i, v)
    return v
    """
    ...


@replacement
def _nat_loop(
    initial: T, n: Int, abstraction: PairType[PairType[NatType, T], T]
) -> DoubleThunkType[T]:
    def replacement():
        v = initial
        for i in range(n.value()):
            v = Apply(abstraction, Pair(nat(i), v))
        return v

    return lambda: NatLoop(initial, n, abstraction), replacement
