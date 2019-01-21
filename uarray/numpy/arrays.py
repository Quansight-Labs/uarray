import numpy
import typing
from ..core import *
from ..dispatch import *
import dataclasses

T_box = typing.TypeVar("T_box", bound=Box)
ctx = MapChainCallable()

# default_context.append(ctx)


# class NumpyDataType(Box[numpy.dtype]):
#     pass


@dataclasses.dataclass
class NumpyScalar(Box[numpy.number]):
    value: numpy.number
    # dtype: NumpyDataType

    def __add__(self, other: "NumpyScalar") -> "NumpyScalar":
        return NumpyScalar(self.value + other.value)


# OPERATION_NAME = "numpy-ndarray"


def is_ndarray(b: Box) -> bool:
    return isinstance(b.value, numpy.ndarray)


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not is_ndarray(self):
        return NotImplemented
    return Array.create_shape(*self.value.shape)


def index_ndarray(array: Array[T_box], idx: List[Nat]) -> T_box:
    ...


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[List[Nat], T_box]:
    if not is_ndarray(self):
        return NotImplemented

    @Array.create_idx_abs
    def idx_abs(idx: List[Nat]) -> T_box:
        return self.dtype._replace(Operation(index_ndarray, (self, idx)))

    return idx_abs


@register(ctx, index_ndarray)
def _index_ndarray(array: Array[T_box], idx: List[Nat]) -> T_box:
    if (
        not is_ndarray(array)
        or not idx._concrete
        or not all(isinstance(i, Nat) and i._concrete for i in idx._args)
    ):
        return NotImplemented

    indices = tuple(i.value for i in idx._args)
    new_array = array.value[indices]
    # How to talk about dtype?
    # How do we talk about inner value of NumPy array?
    # It should be in typing that we are talking about an *array of ...* Where ... is some subset of all boxes
    # Array of NumPy value maybe? So that dtype has to be NumPy scalar?
    # Because all numpy scalars have same methods :)
    @Array.create_idx_abs
    def idx_abs(idx: List[Nat]) -> T_box:
        return self.dtype._replace(Operation("index_ndarray", (self, idx)))

    return idx_abs

