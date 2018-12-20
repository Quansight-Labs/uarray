import typing

from ..machinery import *
from .naturals import *
from .abstractions import *
from .equality import *
from .booleans import *
from .pairs import *
from .lists import *

__all__ = [
    "VecType",
    "vec",
    "VecFirst",
    "VecRest",
    "VecPush",
    "VecConcat",
    "VecDrop",
    "VecTake",
    "VecReverse",
    "VecReduce",
]

T = typing.TypeVar("T")

##
# Types
##

# length, content
VecType = PairType[NatType, ListType[T]]

##
# Helper constructors
##


def vec(*xs: T) -> VecType[T]:
    return Pair(nat(len(xs)), list_(*xs))


##
# Operations
##


@operation_and_replacement
def VecFirst(v: VecType[T]) -> T:
    """
    v[0]
    """
    return ListFirst(Exr(v))


@operation_and_replacement
def VecRest(v: VecType[T]) -> VecType[T]:
    """
    v[1:]
    """
    return Pair(NatDecr(Exl(v)), ListRest(Exr(v)))


@operation_and_replacement
def VecPush(x: T, v: VecType[T]) -> VecType[T]:
    """
    [x] + v
    """
    return Pair(NatIncr(Exl(v)), ListPush(x, Exr(v)))


@operation_and_replacement
def VecConcat(l: VecType[T], r: VecType[T]) -> VecType[T]:
    return Pair(NatAdd(Exl(l), Exl(r)), ListConcat(Exl(l), Exr(l), Exr(r)))


@operation_and_replacement
def VecDrop(n: NatType, v: VecType[T]) -> VecType[T]:
    return Pair(NatSubtract(Exl(v), n), ListDrop(n, Exr(v)))


@operation_and_replacement
def VecTake(n: NatType, v: VecType[T]) -> VecType[T]:
    return Pair(n, Exr(v))


@operation_and_replacement
def VecReverse(v: VecType[T]) -> VecType[T]:
    return Pair(Exl(v), ListReverse(Exl(v), Exr(v)))


@operation_and_replacement
def VecReduce(op: PairType[PairType[T, T], T], initial: T, v: VecType[T]) -> T:
    return ListReduce(op, initial, Exl(v), Exr(v))
