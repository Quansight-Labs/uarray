import typing
import functools
import dataclasses

import numpy
from ..dispatch import *
from ..core import *
from ..moa import *

__all__ = ["LazyNDArray", "to_box", "to_array", "numpy_ufunc"]

ctx = MapChainCallable()
default_context.append(ctx)


@functools.singledispatch
def to_box(a: object) -> Box:
    return Box(a)


@to_box.register
def to_box_box(a: Box) -> Box:
    return a


def to_array(b: Box) -> Array:
    if isinstance(b, Array):
        return b
    elif isinstance(b, LazyNDArray):
        return b.array
    return Array(Operation(to_array, (b,)), Box(None))


@register(ctx, to_array)
def _to_array(b: Box) -> Array:
    if isinstance(b.value, (int, float, complex)):
        return Array.create_0d(b)
    return NotImplemented


T_box = typing.TypeVar("T_box", bound=Box)


def numpy_ufunc(ufunc: Box[numpy.ufunc], *args: Box) -> Box:
    return Box(Operation(numpy_ufunc, (ufunc, *args)))


@dataclasses.dataclass
class LazyNDArray(
    Box[typing.Any], typing.Generic[T_box], numpy.lib.mixins.NDArrayOperatorsMixin
):
    value: typing.Any
    dtype: T_box

    @classmethod
    def create(cls, a: Array[T_box]) -> "LazyNDArray[T_box]":
        return cls(a.value, a.dtype)

    @property
    def array(self) -> Array[T_box]:
        return Array(self.value, self.dtype)

    def sum(self):
        return LazyNDArray.create(
            MoA.from_array(self.array)
            .reduce_abstraction(
                functoools.partial(numpy_ufunc, Box(numpy.add)),
                self.array.dtype._replace(0),
            )
            .array
        )

    def __array_ufunc__(self, ufunc: numpy.ufunc, method: str, *inputs, **kwargs):
        out, = kwargs.pop("out", (None,))
        if kwargs or len(inputs) not in (1, 2) or method not in ("__call__", "outer"):
            return NotImplemented
        array_inputs = map(MoA.from_array, map(to_array, map(to_box, inputs)))
        res: MoA
        op = functools.partial(numpy_ufunc, Box(ufunc))
        if method == "outer":
            a, b = array_inputs
            res = a.outer_product_abstraction(op, b)

        elif len(inputs) == 1:
            a, = array_inputs
            res = a.unary_operation_abstraction(op)
        else:
            a, b = array_inputs
            res = a.binary_operation_abstraction(op, b)
        if out:
            out.box = res.array
        return out or LazyNDArray.create(res.array)

    def __getitem__(self, i: int):
        return LazyNDArray.create(
            MoA.from_array(self.array)[
                MoA.from_array(Array.create_1d_infer(Nat(i)))
            ].array
        )

    @property
    def shape(self) -> typing.Tuple[int, ...]:
        """
        Replace and turn into tuple of integers, because others depend on this API.
        """
        return tuple(i.value for i in replace(self.array.shape.list).value.args)

    def with_dim(self, ndim: Nat) -> "LazyNDArray":
        return LazyNDArray.create(self.array.with_dim(ndim))
