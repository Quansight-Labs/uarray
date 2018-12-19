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
]

T_cov = typing.TypeVar("T_cov")

##
# Types
##

# length, content
VecType = PairType[NatType, ListType[T_cov]]

##
# Helper constructors
##


def vec(*xs: T_cov) -> VecType[T_cov]:
    return Pair(nat(len(xs)), list_(*xs))


##
# Operations
##


@operation_and_replacement
def VecFirst(v: VecType[T_cov]) -> T_cov:
    """
    v[0]
    """
    return ListFirst(Exr(v))


@operation_and_replacement
def VecRest(v: VecType[T_cov]) -> VecType[T_cov]:
    """
    v[1:]
    """
    return Pair(NatDecr(Exl(v)), ListRest(Exr(v)))


@operation_and_replacement
def VecPush(x: T_cov, v: VecType[T_cov]) -> VecType[T_cov]:
    """
    [x] + v
    """
    return Pair(NatIncr(Exl(v)), ListPush(x, Exr(v)))


@operation_and_replacement
def VecConcat(l: VecType[T_cov], r: VecType[T_cov]) -> VecType[T_cov]:
    return Pair(NatAdd(Exl(l), Exl(r)), ListConcat(Exl(l), Exr(l), Exr(r)))


@operation_and_replacement
def VecDrop(n: NatType, v: VecType[T_cov]) -> VecType[T_cov]:
    return Pair(NatSubtract(Exl(v), n), ListDrop(n, Exr(v)))


@operation_and_replacement
def VecTake(n: NatType, v: VecType[T_cov]) -> VecType[T_cov]:
    return Pair(n, Exr(v))
