import typing
import dataclasses
from .dispatch import *
from .core import *


__all__ = ["MoA"]


T_box = typing.TypeVar("T_box", bound=Box)


@dataclasses.dataclass
class MoA(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any
    dtype: T_box

    array: Array[T_box] = dataclasses.field(init=False)

    def __post_init__(self):
        self.array = self._get_array()

    def _get_array(self) -> Array[T_box]:
        return Array(Operation(MoA._get_array, (self,)), self.dtype)

    @property
    def _concrete(self):
        return isinstance(self.value, Operation) and self.value.name == MoA

    @classmethod
    def create(cls, array: Array[T_box]):
        return cls(Operation(MoA, (array,)), array.dtype)

    def dim(self) -> "MoA[Nat]":
        return MoA.create(Array.create_0d(self.array.shape.get_length()))

    def shape(self) -> "MoA[Nat]":
        return MoA.create(Array.from_vec(self.array.shape))

    def __getitem__(self, idxs: "MoA[Nat]") -> "MoA[T_box]":
        n_idxs = idxs.array.shape[Nat(0)]
        new_shape = self.array.shape.drop(n_idxs)

        @Array.create_idx_abs
        def new_idx_abs(idx: List[Nat]) -> T_box:
            return self.array.idx_abs(idxs.array.to_list().concat(idx))

        return MoA.create(Array.create(new_shape, new_idx_abs))


@register(ctx, MoA._get_array)
def _get_array(self: MoA[T_box]) -> Array[T_box]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[0]


# # TODO: Implement broadcasting
# @operation_and_replacement
# def BinaryOperation(
#     op: PairType[PairType[T, U], V], l: ArrayType[T], r: ArrayType[U]
# ) -> ArrayType[V]:
#     @abstraction
#     def new_idx_abstraction(idx: IdxsType) -> V:
#         l_item = Apply(Exr(l), idx)
#         r_item = Apply(Exr(r), idx)
#         return Apply(op, Pair(l_item, r_item))

#     return Pair(Exl(l), new_idx_abstraction)


# # TODO: Make general Add operation that this depends on, so can work for other number types


# @abstraction
# def nat_add_abstraction(p: PairType[NatType, NatType]) -> NatType:
#     return NatAdd(Exl(p), Exr(p))


# @abstraction
# def nat_mult_abstraction(p: PairType[NatType, NatType]) -> NatType:
#     return NatMultiply(Exl(p), Exr(p))


# # TODO: Make transpose generlized for any ordering
# @operation_and_replacement
# def Transpose(a: ArrayType[T]) -> ArrayType[T]:
#     @abstraction
#     def new_idx_abstraction(idx: IdxsType) -> T:
#         dim = Exl(Exl(a))
#         return Apply(Exr(a), ListReverse(dim, idx))

#     return Pair(VecReverse(Exl(a)), new_idx_abstraction)


# @operation_and_replacement
# def Reduce(op: PairType[PairType[T, T], T], initial: T, a: ArrayType[T]):
#     return array_0d(VecReduce(op, initial, Array1DToVec(a)))


# @operation_and_replacement
# def ListGamma(
#     idx: ListType[NatType], shape: ListType[NatType], length: NatType
# ) -> NatType:
#     @abstraction
#     def loop_abstraction(p: PairType[NatType, NatType]) -> NatType:
#         i = Exl(p)
#         val = Exr(p)
#         return NatAdd(Apply(idx, i), NatMultiply(Apply(shape, i), val))

#     return NatLoop(nat(0), length, loop_abstraction)


# @operation_and_replacement
# def ListToArrayND(l: ListType[T], shape: VecType[NatType]) -> ArrayType[T]:
#     """
#     Returns a reshaped array
#     """

#     @abstraction
#     def idx_abstraction(idx: IdxsType) -> T:
#         return Apply(l, ListGamma(idx, Exr(shape), Exl(shape)))

#     return Pair(shape, idx_abstraction)
