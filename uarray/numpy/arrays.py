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
def _get_idx_abs(self: Array[T_box]) -> Abstraction[List[Nat], T_box]:
    if not is_numpy_array(self):
        return NotImplemented

    dim = self.value.ndim

    @Array.create_idx_abs
    def idx_abs(idx: List[Nat]) -> T_box:
        return self.dtype._replace(
            Operation(index_ndarray, (self, *(idx[Nat(d)] for d in range(dim))))
        )

    return idx_abs


@register(ctx, index_ndarray)
def _index_ndarray(array: Array[T_box], *idx: Nat) -> T_box:
    if not is_numpy_array(array) or not all(i._concrete for i in idx):
        return NotImplemented

    return array.dtype._replace(array.value[tuple(i.value for i in idx)])


# def to_numpy_array(a: Array[NumpyScalar]) -> Array[NumpyScalar]:
#     return Array(Operation(to_numpy_array, (a,)), a.dtype)


# @register(ctx, to_numpy_array)
# def _to_numpy_array(a: Array[NumpyScalar]) -> Array[NumpyScalar]:
#     return to_numpy_array_expanded_first(a.shape, a.idx_abs)


# def to_numpy_array_expanded_first(
#     shape: Vec[Nat], idx_abs: Abstraction[List[Nat], NumpyScalar]
# ) -> Array[NumpyScalar]:
#     return Array(
#         Operation(to_numpy_array_expanded_first, (shape, idx_abs)), idx_abs.rettype
#     )


# @register(ctx, to_numpy_array_expanded_first)
# def _to_numpy_array_expanded_first(
#     shape: Vec[Nat], idx_abs: Abstraction[List[Nat], NumpyScalar]
# ) -> Array[NumpyScalar]:
#     if not shape._concrete:
#         return NotImplemented
#     shape_length, shape_list = shape.value.args
#     if not shape_list._concrete:
#         return NotImplemented
#     shape_items: typing.Tuple[Nat, ...] = shape_list.value.args
#     if not all(i._concrete for i in shape_items):
#         return NotImplemented
#     shape_items_ints: typing.Tuple[int, ...] = tuple(i.value for i in shape_items)

#     # iterate through all combinations of shape list
#     # create list that has all of these
#     all_possible_idxs = list(itertools.product(*(range(i) for i in shape_items_ints)))

#     contents = List.create(
#         idx_abs.rettype,
#         *(idx_abs(List.create(Nat(None), *map(Nat, idx))) for idx in all_possible_idxs)
#     )

#     return to_python_array_expanded(shape, contents)
