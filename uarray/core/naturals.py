from ..machinery import *
from .booleans import *
from .equality import *

__all__ = ["NatType", "nat", "NatLTE", "NatIncr", "NatDecr", "NatAdd", "NatSubtract"]


class NatType:
    """
    Natural number
    """

    pass


def nat(i: int) -> NatType:
    return Int(i)


class Int(Symbol[int], NatType):
    """
    Natural number represented by python integer
    """

    pass


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


@operation
def NatSubtract(l: NatType, r: NatType) -> NatType:
    ...


@replacement
def _nat_subtract(l: Int, r: Int) -> DoubleThunkType[NatType]:
    return lambda: NatSubtract(l, r), lambda: Int(l.value() - r.value())
