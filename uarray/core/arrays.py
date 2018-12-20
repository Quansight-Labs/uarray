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
    "VecToArray1D",
    "Array1DToVec",
    "Array1DToList",
    "Array0DToInner",
]
T = typing.TypeVar("T")

##
# Types
##

ShapeType = VecType[NatType]

IdxsType = ListType[NatType]
# mapping from indices to values
IdxAbstractionType = PairType[IdxsType, T]

ArrayType = PairType[ShapeType, IdxAbstractionType[T]]


##
# Helper constructors
##


def array_0d(x: T) -> ArrayType[T]:
    """
    Returns a scalar array of `x`.
    """
    return Pair(vec(), const_abstraction(x))


def array_1d(*xs: T) -> ArrayType[T]:
    """
    Returns a vector array of `xs`.
    """
    return VecToArray1D(vec(*xs))


@operation_and_replacement
def VecToArray1D(v: VecType[T]) -> ArrayType[T]:
    """
    Returns a 1D array that has contents of the vector.
    """

    @abstraction
    def idx_abstraction(idx: IdxsType) -> T:
        return Apply(Exr(v), ListFirst(idx))

    return Pair(vec(Exl(v)), idx_abstraction)


@operation_and_replacement
def Array1DToList(a: ArrayType[T]) -> ListType[T]:
    """
    Returns a vector from a 1D array
    """

    @abstraction
    def content(vec_idx: NatType) -> T:
        return Apply(Exr(a), list_(vec_idx))

    return content


@operation_and_replacement
def Array1DToVec(a: ArrayType[T]) -> VecType[T]:
    """
    Returns a vector from a 1D array
    """
    return Pair(VecFirst(Exl(a)), Array1DToList(a))


@operation_and_replacement
def Array0DToInner(a: ArrayType[T]) -> T:
    """
    Returns a vector from a 1D array
    """
    idxs: ListType[NatType] = list_()
    return Apply(Exr(a), idxs)
