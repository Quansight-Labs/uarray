from .functions import *


class NatType:
    """
    Natural number
    """

    pass


class Int(Symbol[int], NatType):
    """
    Natural number represented by python integer
    """

    pass


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
