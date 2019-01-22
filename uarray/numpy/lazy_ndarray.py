import typing
import functools

import numpy
from ..dispatch import *
from ..core import *
from ..moa import *
from .arrays import *

__all__ = ["LazyNDArray"]

ctx = MapChainCallable()
default_context.append(ctx)

# @functools.singledispatch
# def to_box(a: object) -> Box:
#     return Box(a)


# @to_box.register
# def to_box_box(b: Box) -> Box:
#     return b


@functools.singledispatch
def to_array(a: object) -> Array:
    raise NotImplementedError(f"{type(a)}")


@to_array.register
def to_array_array(a: Array) -> Array:
    return a


@to_array.register
def to_array_int(a: int) -> Array[Box[int]]:
    return Array.create_0d(Box(a))


@to_array.register
def to_array_float(a: float) -> Array[Box[float]]:
    return Array.create_0d(Box(a))


@to_array.register
def to_array_complex(a: complex) -> Array[Box[complex]]:
    return Array.create_0d(Box(a))


@to_array.register
def to_array_ndarray(a: numpy.ndarray) -> Array:
    return create_numpy_array(a)


# TODO: Maybe make box somehow?
class LazyNDArray(numpy.lib.mixins.NDArrayOperatorsMixin):
    def __init__(self, box: Array) -> None:
        self.box = box

    def __repr__(self):
        return f"LazyNDArray({repr(self.box)})"

    def __str__(self):
        return f"LazyNDArray({str(self.box)})"

    def __array_ufunc__(self, ufunc: numpy.ufunc, method: str, *inputs, **kwargs):
        if kwargs or len(inputs) not in (1, 2) or method != "__call__":
            return NotImplemented
        array_inputs = map(to_array, inputs)
        if len(inputs) == 1:
            a, = array_inputs
            return LazyNDArray(
                unary_operation_abstraction(
                    Abstraction.create(lambda v: Box(Operation(ufunc, (v,))), a.dtype),
                    a,
                )
            )
        a, b = array_inputs
        return LazyNDArray(
            binary_operation_abstraction(
                a,
                Abstraction.create_bin(
                    lambda l, r: Box(Operation(ufunc, (l, r))), a.dtype, b.dtype
                ),
                b,
            )
        )

    @property
    def shape(self) -> typing.Tuple[int, ...]:
        """
        Replace and turn into tuple of integers, because others depend on this API.
        """
        return tuple(i.value for i in replace(self.box.shape.list).value.args)


@to_array.register
def to_array_lazy_ndarray(a: LazyNDArray) -> Array:
    return a.box
