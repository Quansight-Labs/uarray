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
]

T_cov = typing.TypeVar("T_cov")

##
# Types
##

# Lists are mappings from integers to values
ListType = PairType[NatType, T_cov]

##
# Helper constructors
##


def list_(*xs: T_cov) -> ListType[T_cov]:
    v = never_abstraction
    for x in xs[::-1]:
        v = ListPush(x, v)
    return v


##
# Operations
##


@operation_and_replacement
def ListFirst(l: ListType[T_cov]) -> T_cov:
    """
    v[0]
    """
    return Apply(l, nat(0))


@operation_and_replacement
def ListRest(l: ListType[T_cov]) -> ListType[T_cov]:
    """
    v[1:]
    """

    def new_list(idx: NatType) -> T_cov:
        return Apply(l, NatIncr(idx))

    return abstraction(new_list)


@operation_and_replacement
def ListPush(x: T_cov, l: ListType[T_cov]) -> ListType[T_cov]:
    """
    [x] + v
    """

    def new_list(idx: NatType) -> T_cov:
        return If(Equal(idx, nat(0)), x, Apply(l, NatDecr(idx)))

    return abstraction(new_list)


@operation_and_replacement
def ListConcat(
    l_length: NatType, l: ListType[T_cov], r: ListType[T_cov]
) -> ListType[T_cov]:
    """
    l + r
    """

    def new_list(idx: NatType) -> T_cov:
        return If(
            NatLTE(idx, l_length), Apply(l, idx), Apply(r, (NatSubtract(idx, l_length)))
        )

    return abstraction(new_list)


@operation_and_replacement
def ListDrop(n: NatType, l: ListType[T_cov]) -> ListType[T_cov]:
    """
    l[n:]
    """

    def new_list(idx: NatType) -> T_cov:
        return Apply(l, NatAdd(idx, n))

    return abstraction(new_list)
