import typing
import functools

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
    ...


class LazyNDArray(
    Box[Operation[typing.Tuple[Array[T_box]]]],
    typing.Generic[T_box],
    numpy.lib.mixins.NDArrayOperatorsMixin,
):
    @classmethod
    def create(cls, a: Array[T_box]) -> "LazyNDArray[T_box]":
        if not isinstance(a, Array):
            raise TypeError
        return cls(Operation(LazyNDArray, (a,)))

    @property
    def array(self) -> Array[T_box]:
        return self.value.args[0]

    def sum(self):
        return LazyNDArray.create(
            reduce(
                self.array,
                Abstraction.create_bin(
                    lambda l, r: Box(Operation(numpy_ufunc, (Box(numpy.add), l, r))),
                    self.array.dtype._replace(None),
                    self.array.dtype._replace(None),
                ),
                self.array.dtype._replace(0),
            )
        )

    def __array_ufunc__(self, ufunc: numpy.ufunc, method: str, *inputs, **kwargs):
        out, = kwargs.pop("out", (None,))
        if kwargs or len(inputs) not in (1, 2) or method not in ("__call__", "outer"):
            return NotImplemented
        array_inputs = map(to_array, map(to_box, inputs))
        res: Array
        if method == "outer":
            a, b = array_inputs
            res = outer_product(
                a,
                Abstraction.create_bin(
                    lambda l, r: Box(Operation(numpy_ufunc, (Box(ufunc), l, r))),
                    a.dtype._replace(None),
                    b.dtype._replace(None),
                ),
                b,
            )

        elif len(inputs) == 1:
            a, = array_inputs
            res = unary_operation_abstraction(
                Abstraction.create(
                    lambda v: Box(Operation(numpy_ufunc, (Box(ufunc), v))),
                    a.dtype._replace(None),
                ),
                a,
            )
        else:
            a, b = array_inputs
            res = binary_operation_abstraction(
                a,
                Abstraction.create_bin(
                    lambda l, r: Box(Operation(numpy_ufunc, (Box(ufunc), l, r))),
                    a.dtype._replace(None),
                    b.dtype._replace(None),
                ),
                b,
            )
        if out:
            out.box = res
        return out or LazyNDArray.create(res)

    def __getitem__(self, i: int):
        return LazyNDArray.create(index(Array.create_1d_infer(Nat(i)), self.array))

    @property
    def shape(self) -> typing.Tuple[int, ...]:
        """
        Replace and turn into tuple of integers, because others depend on this API.
        """
        return tuple(i.value for i in replace(self.array.shape.list).value.args)

    def with_dim(self, ndim: Nat) -> "LazyNDArray":
        return LazyNDArray.create(self.array.with_dim(ndim))
