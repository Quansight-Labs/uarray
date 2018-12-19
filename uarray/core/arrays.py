import typing

from ..machinery import *
from .naturals import *
from .vectors import *
from .abstractions import *
from .lists import *
from .pairs import *

__all__ = [
    "ShapeType",
    "IdxsType",
    "IdxAbstractionType",
    "ArrayType",
    "array_0d",
    "array_1d",
    "VecToArray",
    "ArrayToVec",
]
T_cov = typing.TypeVar("T_cov")

##
# Types
##

ShapeType = VecType[NatType]

IdxsType = ListType[NatType]
# mapping from indices to values
IdxAbstractionType = PairType[IdxsType, T_cov]

ArrayType = PairType[ShapeType, IdxAbstractionType[T_cov]]


##
# Helper constructors
##


def array_0d(x: T_cov) -> ArrayType[T_cov]:
    """
    Returns a scalar array of `x`.
    """
    return Pair(vec(), const_abstraction(x))


def array_1d(*xs: T_cov) -> ArrayType[T_cov]:
    """
    Returns a vector array of `xs`.
    """
    return VecToArray(vec(*xs))


@operation_and_replacement
def VecToArray(v: VecType[T_cov]) -> ArrayType[T_cov]:
    """
    Returns a 1D array that has contents of the vector.
    """

    @abstraction
    def idx_abstraction(idx: IdxsType) -> T_cov:
        return Apply(Exr(v), ListFirst(idx))

    return Pair(vec(Exl(v)), idx_abstraction)


@operation_and_replacement
def ArrayToVec(a: ArrayType[T_cov]) -> VecType[T_cov]:
    """
    Returns a vector from a 1D array
    """
    length = VecFirst(Exl(a))

    @abstraction
    def content(vec_idx: NatType) -> T_cov:
        return Apply(Exr(a), list_(vec_idx))

    return Pair(length, content)
