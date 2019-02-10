import dataclasses
import typing

from .abstractions import *
from .context import *
from .lists import *
from .naturals import *
from .vectors import *
from ..dispatch import *

__all__ = ["Array"]

T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


@dataclasses.dataclass
class Array(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any = None
    dtype: T_box = typing.cast(T_box, Box())

    @property
    def shape(self) -> Vec[Nat]:
        return self._get_shape()

    @property
    def idx_abs(self) -> Abstraction[Vec[Nat], T_box]:
        return self._get_idx_abs()

    @operation
    def _get_shape(self) -> Vec[Nat]:
        return Vec(dtype=Nat())

    @operation
    def _get_idx_abs(self) -> Abstraction[Vec[Nat], T_box]:
        return Abstraction(rettype=self.dtype)

    @staticmethod
    @concrete_operation
    def create(
        shape: Vec[Nat], idx_abs: Abstraction[Vec[Nat], T_box]
    ) -> "Array[T_box]":
        return Array(dtype=idx_abs.rettype)

    @classmethod
    def create_0d(cls, x: T_box) -> "Array[T_box]":
        """
        Returns a scalar array of `x`.
        """
        return cls.create(
            Vec.create_args(Nat(None)), Abstraction.create(lambda _: x, x.replace(None))
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
        def idx_fn(idxs: Vec[Nat]) -> T_box:
            return vec[idxs.first()]

        return Array.create(Vec.create_infer(vec.length), idx_fn)

    @classmethod
    def create_idx_abs(
        cls, fn: typing.Callable[[Vec[Nat]], T_box]
    ) -> Abstraction[Vec[Nat], T_box]:
        return Abstraction.create(fn, Vec(None, Nat(None)))

    @classmethod
    def create_shape(cls, *xs: Nat) -> Vec[Nat]:
        return Vec.create_args(Nat(None), *xs)

    def __getitem__(self, idx: Vec[Nat]) -> T_box:
        """
        Use the shape to know the length of the indices.

        Instead we could have users pass in list instead of vector.
        But this causes some assymetry in creating and use the index abstraction.
        """
        return self.idx_abs(Vec.create(self.shape.length, idx.list))

    def to_list(self) -> List[T_box]:
        def fn(i: Nat) -> T_box:
            return self[Array.create_shape(i)]

        return List.from_abstraction(Abstraction.create(fn, Nat(None)))

    def to_vec(self) -> Vec[T_box]:
        return Vec.create(self.shape[Nat(0)], self.to_list())

    def to_value(self) -> T_box:
        return self[self.create_shape()]

    def with_dim(self, ndim: Nat) -> "Array[T_box]":
        return Array.create(self.shape.with_length(ndim), self.idx_abs)


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not isinstance(self.value, Operation) or not self.value.name == Array.create:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[Vec[Nat], T_box]:
    if not isinstance(self.value, Operation) or not self.value.name == Array.create:
        return NotImplemented
    return self.value.args[1]
