import typing
import functools


from .typing import *
from .helpers import *
from .abstract import *

__all__ = [
    "naturals_take",
    "naturals_drop",
    "naturals_concat",
    "index",
    "shape",
    "dim",
    "reduce",
    "iota",
    "outer_product",
]

T = typing.TypeVar("T")
V = typing.TypeVar("V")
R = typing.TypeVar("R")


def naturals_take(n: Naturals, i: int) -> Naturals:
    """
    n[:i]
    """
    return AbstractNaturals(i, n.__getitem__)


def naturals_drop(n: Naturals, i: int) -> Naturals:
    """
    n[i:]
    """

    def getitem(idx: int) -> int:
        return n[idx + i]

    return AbstractNaturals(len(n) - i, getitem)


def naturals_concat(l: Naturals, r: Naturals) -> Naturals:
    """
    l + r
    """

    def getitem(i: int):
        if i < len(l):
            return l[i]
        return r[i - len(l)]

    return AbstractNaturals(len(l) + len(r), getitem)


def index(idx: Array[int], a: Array[T]) -> Array[T]:
    new_shape = naturals_drop(u_shape(a), u_shape(idx)[0])

    idx_naturals = AbstractNaturals.from_array(idx)

    def index_fn(inner_idx: Naturals) -> T:
        total_idx = naturals_concat(idx_naturals, inner_idx)
        return u_psi(a, total_idx)

    return AbstractArray(new_shape, index_fn, u_mtype(a))


def shape(a: Array[T]) -> Array[int]:
    return AbstractArray.from_naturals(u_shape(a))


def dim(a: Array[T]) -> Array[int]:
    return AbstractArray.from_value(len(u_shape(a)), int)


def reduce(
    fn: typing.Callable[[Array[T], Array[T]], Array[T]], initial: Array[T], a: Array[T]
) -> Array[T]:
    value = initial
    for i in range(u_shape(a)[0]):
        value = fn(value, index(AbstractArray.from_value(i, int), a))
    return value


def iota(a: Array[int]) -> Array[int]:
    assert is_scalar(a)

    n = u_psi(a, AbstractNaturals.empty())
    return AbstractArray(AbstractNaturals.from_value(n), lambda idxs: idxs[0], int)


@functools.singledispatch
def outer_product(
    l: Array[T], r: Array[V], op: typing.Callable[[T, V], R], mtype: typing.Type[R]
) -> Array[R]:
    first_dim = len(u_shape(l))

    def index_fn(idx: Naturals) -> R:
        l_idx = naturals_take(idx, first_dim)
        r_idx = naturals_drop(idx, first_dim)
        return op(u_psi(l, l_idx), u_psi(r, r_idx))

    return AbstractArray(naturals_concat(u_shape(l), u_shape(r)), index_fn, mtype)
