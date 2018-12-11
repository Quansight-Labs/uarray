import functools
import typing

import numpy

from .typing import *
from .helpers import *
from .abstract import *
from .moa import *

__all__ = ["NumpyArray", "to_numpy_array"]
T = typing.TypeVar("T")


def naturals_to_tuple(n: Naturals) -> typing.Tuple[int, ...]:
    t: typing.Tuple[int, ...] = ()
    for i in range(len(n)):
        t += (n[i],)
    return t


class NumpyArray(Array[T]):
    def __init__(self, a: numpy.ndarray):
        self.a = a

    def __u_shape__(self) -> Naturals:
        return self.a.shape

    def __u_psi__(self, indxs: Naturals) -> T:
        return self.a[naturals_to_tuple(indxs)]

    def __u_mtype__(self) -> typing.Type[T]:
        return getattr(numpy, self.a.dtype.name)


@functools.singledispatch
def to_numpy_array(a: Array[T], nd: numpy.ndarray = None) -> numpy.ndarray:
    if nd is None:
        nd = numpy.empty(naturals_to_tuple(u_shape(a)), u_mtype(a))
    if is_scalar(a):
        nd[()] = u_psi(a, AbstractNaturals.empty())
    else:
        for i in range(u_shape(a)[0]):
            idx = AbstractArray.from_naturals(AbstractNaturals.from_value(i))
            to_numpy_array(index(idx, a), nd[i, ...])
    return nd


@to_numpy_array.register
def _to_numpy_array_numpy(a: NumpyArray) -> numpy.ndarray:
    return a.a
