import typing
from .machinery import *
from .core import *


__all__ = [
    "Shape",
    "Index",
    "Dim",
    "BinaryOperation",
    "nat_add_abstraction",
    "nat_mult_abstraction",
    "ListToArrayND",
    "Transpose",
    "Reduce",
]

T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")


@operation_and_replacement
def Dim(a: ArrayType[T]) -> ArrayType[NatType]:
    return array_0d(Exl(Exl(a)))


@operation_and_replacement
def Shape(a: ArrayType[T]) -> ArrayType[NatType]:
    return VecToArray1D(Exl(a))


@operation_and_replacement
def Index(idxs: ArrayType[NatType], a: ArrayType[T]) -> ArrayType[T]:
    idxs_shape = Exl(idxs)
    n_idxs = Apply(Exr(idxs_shape), nat(0))
    new_shape = VecDrop(n_idxs, Exl(a))

    @abstraction
    def new_idx_abstraction(idx: IdxsType) -> T:
        return Apply(Exr(a), ListConcat(n_idxs, Array1DToList(idxs), idx))

    return Pair(new_shape, new_idx_abstraction)


# TODO: Implement broadcasting
@operation_and_replacement
def BinaryOperation(
    op: PairType[PairType[T, U], V], l: ArrayType[T], r: ArrayType[U]
) -> ArrayType[V]:
    @abstraction
    def new_idx_abstraction(idx: IdxsType) -> V:
        l_item = Apply(Exr(l), idx)
        r_item = Apply(Exr(r), idx)
        return Apply(op, Pair(l_item, r_item))

    return Pair(Exl(l), new_idx_abstraction)


# TODO: Make general Add operation that this depends on, so can work for other number types


@abstraction
def nat_add_abstraction(p: PairType[NatType, NatType]) -> NatType:
    return NatAdd(Exl(p), Exr(p))


@abstraction
def nat_mult_abstraction(p: PairType[NatType, NatType]) -> NatType:
    return NatMultiply(Exl(p), Exr(p))


# TODO: Make transpose generlized for any ordering
@operation_and_replacement
def Transpose(a: ArrayType[T]) -> ArrayType[T]:
    @abstraction
    def new_idx_abstraction(idx: IdxsType) -> T:
        dim = Exl(Exl(a))
        return Apply(Exr(a), ListReverse(dim, idx))

    return Pair(VecReverse(Exl(a)), new_idx_abstraction)


@operation_and_replacement
def Reduce(op: PairType[PairType[T, T], T], initial: T, a: ArrayType[T]):
    return array_0d(VecReduce(op, initial, Array1DToVec(a)))


@operation_and_replacement
def ListGamma(
    idx: ListType[NatType], shape: ListType[NatType], length: NatType
) -> NatType:
    @abstraction
    def loop_abstraction(p: PairType[NatType, NatType]) -> NatType:
        i = Exl(p)
        val = Exr(p)
        return NatAdd(Apply(idx, i), NatMultiply(Apply(shape, i), val))

    return NatLoop(nat(0), length, loop_abstraction)


@operation_and_replacement
def ListToArrayND(l: ListType[T], shape: VecType[NatType]) -> ArrayType[T]:
    """
    Returns a reshaped array
    """

    @abstraction
    def idx_abstraction(idx: IdxsType) -> T:
        return Apply(l, ListGamma(idx, Exr(shape), Exl(shape)))

    return Pair(shape, idx_abstraction)
