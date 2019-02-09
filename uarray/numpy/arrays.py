"""
Support reading from NumPy arrays.
"""

import numpy
import typing
from ..core import *
from ..dispatch import *
import dataclasses

from .lazy_ndarray import to_array

__all__: typing.List[str] = []
T_box = typing.TypeVar("T_box", bound=Box)
ctx = MapChainCallable()
default_context.append(ctx)


class NumpyDataType(Box[numpy.dtype]):
    pass


@dataclasses.dataclass
class NumpyScalar(Box[typing.Any]):
    value: typing.Any
    dtype: NumpyDataType


def is_numpy_array(a: Box) -> bool:
    return isinstance(a.value, numpy.ndarray)


@register(ctx, to_array)
def to_array(b: Box) -> Array:
    if not is_numpy_array(b):
        return NotImplemented
    return Array(b.value, NumpyScalar(None, NumpyDataType(b.value.dtype)))


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not is_numpy_array(self):
        return NotImplemented
    return Array.create_shape(*map(Nat, self.value.shape))


def index_ndarray(array: Array[T_box], *idx: Nat) -> T_box:
    ...


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[Vec[Nat], T_box]:
    if not is_numpy_array(self):
        return NotImplemented

    dim = self.value.ndim

    @Array.create_idx_abs
    def idx_abs(idx: Vec[Nat]) -> T_box:
        return self.dtype.replace(
            Operation(index_ndarray, (self, *(idx[Nat(d)] for d in range(dim))))
        )

    return idx_abs


@register(ctx, index_ndarray)
def _index_ndarray(array: Array[T_box], *idx: Nat) -> T_box:
    if not is_numpy_array(array) or not all(isinstance(i.value, int) for i in idx):
        return NotImplemented

    return array.dtype.replace(array.value[tuple(i.value for i in idx)])
