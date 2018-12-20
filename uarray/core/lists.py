import typing

from ..machinery import *
from .naturals import *
from .abstractions import *
from .equality import *
from .booleans import *
from .pairs import *

__all__ = [
    "ListType",
    "list_",
    "ListFirst",
    "ListRest",
    "ListPush",
    "ListConcat",
    "ListDrop",
    "ListReverse",
    "ListReduce",
]

T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")

##
# Types
##

# Lists are mappings from integers to values
ListType = PairType[NatType, T]

##
# Helper constructors
##


def list_(*xs: T) -> ListType[T]:
    v = never_abstraction
    for x in xs[::-1]:
        v = ListPush(x, v)
    return v


##
# Operations
##


@operation_and_replacement
def ListFirst(l: ListType[T]) -> T:
    """
    v[0]
    """
    return Apply(l, nat(0))


@operation_and_replacement
def ListRest(l: ListType[T]) -> ListType[T]:
    """
    v[1:]
    """

    def new_list(idx: NatType) -> T:
        return Apply(l, NatIncr(idx))

    return abstraction(new_list)


@operation_and_replacement
def ListPush(x: T, l: ListType[T]) -> ListType[T]:
    """
    [x] + v
    """

    def new_list(idx: NatType) -> T:
        return If(Equal(idx, nat(0)), x, Apply(l, NatDecr(idx)))

    return abstraction(new_list)


@operation_and_replacement
def ListConcat(l_length: NatType, l: ListType[T], r: ListType[T]) -> ListType[T]:
    """
    l + r
    """

    def new_list(idx: NatType) -> T:
        return If(
            NatLT(idx, l_length), Apply(l, idx), Apply(r, (NatSubtract(idx, l_length)))
        )

    return abstraction(new_list)


@operation_and_replacement
def ListDrop(n: NatType, l: ListType[T]) -> ListType[T]:
    """
    l[n:]
    """

    def new_list(idx: NatType) -> T:
        return Apply(l, NatAdd(idx, n))

    return abstraction(new_list)


@operation_and_replacement
def ListReverse(n: NatType, l: ListType[T]) -> ListType[T]:
    """
    l[::-1]
    """

    def new_list(idx: NatType) -> T:
        return Apply(l, NatDecr(NatSubtract(n, idx)))

    return abstraction(new_list)


@operation_and_replacement
def ListReduce(
    op: PairType[PairType[T, T], T], initial: T, length: NatType, l: ListType[T]
) -> T:
    @abstraction
    def loop_abstraction(index_val_pair):
        idx = Exl(index_val_pair)
        val = Exr(index_val_pair)
        return Apply(op, Pair(Apply(l, idx), val))

    return NatLoop(initial, length, loop_abstraction)
