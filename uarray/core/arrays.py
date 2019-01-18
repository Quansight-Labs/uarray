import typing
import dataclasses

from ..dispatch import *
from .context import *
from .booleans import *
from .abstractions import *
from .naturals import *
from .lists import *
from .vectors import *


__all__ = ["Array"]

T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


@dataclasses.dataclass
class Array(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any
    dtype: T_box

    @property
    def _concrete(self):
        return isinstance(self.value, Operation) and self.value.name == Array

    def get_shape(self) -> Vec[Nat]:
        return Vec(Operation(Array.get_shape, (self,)), Nat(None))

    def get_idx_abs(self) -> Abstraction[List[Nat], T_box]:
        return Abstraction(Operation(Array.get_idx_abs, (self,)), self.dtype)

    @classmethod
    def create(
        cls, shape: Vec[Nat], idx_abs: Abstraction[List[Nat], T_box]
    ) -> "Array[T_box]":
        return cls(Operation(Array, (shape, idx_abs)), idx_abs.rettype)

    @classmethod
    def create_0d(cls, x: T_box) -> "Array[T_box]":
        """
        Returns a scalar array of `x`.
        """
        return cls.create(Vec.create_args(Nat(None)), Abstraction.const(x))

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
        return cls.create_1d(x._replace(None), x, *xs)

    @classmethod
    def from_vec(cls, vec: Vec[T_box]) -> "Array[T_box]":
        def idx_fn(idxs: List[Nat]) -> T_box:
            return vec[idxs.first()]

        return Array.create(
            shape=Vec.create_infer(vec.get_length()),
            idx_abs=Abstraction.create(idx_fn, List(None, Nat(None))),
        )

    def to_list(self) -> List[T_box]:
        idx_abs = self.get_idx_abs()

        def fn(value: List[T_box], i: Nat) -> List[T_box]:
            return value.append(idx_abs(List.create(Nat(None), i)))

        return self.get_shape()[Nat(0)].loop(
            List.create(self.dtype),
            Abstraction.create_bin(fn, List(None, self.dtype), Nat(None)),
        )

    def to_vec(self) -> Vec[T_box]:
        return Vec.create(self.get_shape()[Nat(0)], self.to_list())


@register(ctx, Array.get_shape)
def get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Array.get_idx_abs)
def get_idx_abs(self: Array[T_box]) -> Abstraction[List[Nat], T_box]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[1]


# @operation_and_replacement
# def Array0DToInner(a: ArrayType[T]) -> T:
#     """
#     Returns a vector from a 1D array
#     """
#     idxs: ListType[NatType] = list_()
#     return Apply(Exr(a), idxs)
