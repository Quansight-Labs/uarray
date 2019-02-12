import dataclasses
import typing
import operator

from .abstractions import *
from .context import *
from .lists import *
from .naturals import *
from .vectors import *
from .pairs import *
from ..dispatch import *

__all__ = ["Array"]

T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


@dataclasses.dataclass
class Array(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any = None
    dtype: T_box = typing.cast(T_box, Box())

    @property
    def shape(self) -> Vec[Natural]:
        return self._get_shape()

    @property
    def idx_abs(self) -> Abstraction[Vec[Natural], T_box]:
        return self._get_idx_abs()

    @operation
    def _get_shape(self) -> Vec[Natural]:
        return Vec(dtype=Natural())

    @operation
    def _get_idx_abs(self) -> Abstraction[Vec[Natural], T_box]:
        return Abstraction(rettype=self.dtype)

    @staticmethod
    @concrete_operation
    def create(
        shape: Vec[Natural], idx_abs: Abstraction[Vec[Natural], T_box]
    ) -> "Array[T_box]":
        return Array(dtype=idx_abs.rettype)

    @classmethod
    def create_0d(cls, x: T_box) -> "Array[T_box]":
        """
        Returns a scalar array of `x`.
        """
        return cls.create(
            Vec.create_args(Natural()), Abstraction.create(lambda _: x, x.replace(None))
        )

    @classmethod
    def create_1d(cls, x: T_box, *xs: T_box) -> "Array[T_box]":
        """
        Returns a vector array of `xs`.
        """
        return cls.from_vec(Vec.create_args(x, *xs))

    @classmethod
    def create_1d_infer(cls, x: T_box, *xs: T_box) -> "Array[T_box]":
        """
        Returns a vector array of `xs`.
        """
        return cls.create_1d(x.replace(None), x, *xs)

    @classmethod
    def from_vec(cls, vec: Vec[T_box]) -> "Array[T_box]":
        @cls.create_idx_abs
        def idx_fn(idxs: Vec[Natural]) -> T_box:
            return vec[idxs.first()]

        return Array.create(Vec.create_infer(vec.length), idx_fn)

    @classmethod
    def create_idx_abs(
        cls, fn: typing.Callable[[Vec[Natural]], T_box]
    ) -> Abstraction[Vec[Natural], T_box]:
        return Abstraction.create(fn, Vec(None, Natural()))

    @classmethod
    def create_shape(cls, *xs: Natural) -> Vec[Natural]:
        return Vec.create_args(Natural(), *xs)

    def __getitem__(self, idx: Vec[Natural]) -> T_box:
        """
        Use the shape to know the length of the indices.

        Instead we could have users pass in list instead of vector.
        But this causes some assymetry in creating and use the index abstraction.
        """
        return self.idx_abs(Vec.create(self.shape.length, idx.list))

    @operation_with_default(ctx)
    def size(self) -> Natural:
        return self.shape.reduce_fn(Natural(1), operator.mul)

    def to_list(self) -> List[T_box]:
        def fn(i: Natural) -> T_box:
            return self[Array.create_shape(i)]

        return List.from_abstraction(Abstraction.create(fn, Natural()))

    def to_vec(self) -> Vec[T_box]:
        return Vec.create(self.shape[Natural(0)], self.to_list())

    def to_value(self) -> T_box:
        return self[self.create_shape()]

    def with_dim(self, ndim: Natural) -> "Array[T_box]":
        return Array.create(self.shape.with_length(ndim), self.idx_abs)

    @operation_with_default(ctx)
    def ravel(self) -> "Vec[T_box]":
        return Vec.create(
            self.size(),
            List.create_abstraction(lambda i: self[self.gamma_inverse(i, self.shape)]),
        )

    @staticmethod
    @operation_with_default(ctx)
    def gamma(idx: Vec[Natural], shape: Vec[Natural]) -> Natural:
        def loop_abs(val: Natural, i: Natural) -> Natural:
            return idx[i] + (shape[i] * val)

        return shape.length.loop(
            Natural(0), Abstraction.create_bin(loop_abs, Natural(), Natural())
        )

    @staticmethod
    @operation_with_default(ctx)
    def gamma_inverse(i: Natural, shape: Vec[Natural]) -> Vec[Natural]:
        def loop_abs(
            val: Pair[Natural, Vec[Natural]], i: Natural
        ) -> Pair[Natural, Vec[Natural]]:
            dim = shape.reverse()[i]
            return Pair.create(val.left // dim, val.right.push(val.left % dim))

        return shape.length.loop_abstraction(
            Pair.create(i, Vec.create_args(Natural())), loop_abs
        ).right

    @staticmethod
    @operation_with_default(ctx)
    def from_list_nd(data: List[T_box], shape: Vec[Natural]) -> "Array[T_box]":
        @Array.create_idx_abs
        def idx_abs(idx: Vec[Natural]) -> T_box:
            return data[Array.gamma(idx, shape)]

        return Array.create(shape, idx_abs)


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Natural]:
    if not isinstance(self.value, Operation) or not self.value.name == Array.create:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[Vec[Natural], T_box]:
    if not isinstance(self.value, Operation) or not self.value.name == Array.create:
        return NotImplemented
    return self.value.args[1]
