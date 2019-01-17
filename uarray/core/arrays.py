import typing

from ..dispatch import *
from .context import *
from .booleans import *
from .abstractions import *
from .naturals import *
from .lists import *
from .vectors import *


__all__ = []

T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


Shape = Vec[Nat]
Idxs = List[Nat]
IdxAbstraction = Abstraction[Idxs, T_box]
ArrayOperation = Operation[typing.Tuple[Shape, IdxAbstraction[T_box]]]


class Array(Box[ArrayOperation[T_box]], typing.Generic[T_box]):
    @classmethod
    def create(cls, shape: Shape, idx_abs: IdxAbstraction[T_box]) -> "Array[T_box]":
        return cls(Operation(Array, (shape, idx_abs)))

    @classmethod
    def create_0d(cls, x: T_box) -> "Array[T_box]":
        """
        Returns a scalar array of `x`.
        """
        return cls.create(Vec.create_args(Nat), Abstraction.const(x))

    @classmethod
    def from_vec(cls, vec: Vec[T_box]) -> "Array[T_box]":
        def idx_fn(idxs: Idxs) -> T_box:
            return vec[idxs.first()]

        return Array.create(
            shape=Vec.create_infer(vec._length),
            idx_abs=Abstraction.create(
                idx_fn, lambda v: List.create(Nat, ListContents(v))
            ),
        )


# def array_1d(*xs: T) -> ArrayType[T]:
#     """
#     Returns a vector array of `xs`.
#     """
#     return VecToArray1D(vec(*xs))


# @operation_and_replacement
# def VecToArray1D(v: VecType[T]) -> ArrayType[T]:
#     """
#     Returns a 1D array that has contents of the vector.
#     """

#     @abstraction
#     def idx_abstraction(idx: IdxsType) -> T:
#         return Apply(Exr(v), ListFirst(idx))

#     return Pair(vec(Exl(v)), idx_abstraction)


# @operation_and_replacement
# def Array1DToList(a: ArrayType[T]) -> ListType[T]:
#     """
#     Returns a vector from a 1D array
#     """

#     @abstraction
#     def content(vec_idx: NatType) -> T:
#         return Apply(Exr(a), list_(vec_idx))

#     return content


# @operation_and_replacement
# def Array1DToVec(a: ArrayType[T]) -> VecType[T]:
#     """
#     Returns a vector from a 1D array
#     """
#     return Pair(VecFirst(Exl(a)), Array1DToList(a))


# @operation_and_replacement
# def Array0DToInner(a: ArrayType[T]) -> T:
#     """
#     Returns a vector from a 1D array
#     """
#     idxs: ListType[NatType] = list_()
#     return Apply(Exr(a), idxs)
