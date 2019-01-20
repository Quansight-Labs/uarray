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

    shape: Vec[Nat] = dataclasses.field(init=False)
    idx_abs: Abstraction[List[Nat], T_box] = dataclasses.field(init=False)

    @property
    def _concrete(self):
        return isinstance(self.value, Operation) and self.value.name == Array

    def __post_init__(self):
        self.shape = self._get_shape()
        self.idx_abs = self._get_idx_abs()

    def _get_shape(self) -> Vec[Nat]:
        return Vec(Operation(Array._get_shape, (self,)), Nat(None))

    def _get_idx_abs(self) -> Abstraction[List[Nat], T_box]:
        return Abstraction(Operation(Array._get_idx_abs, (self,)), self.dtype)

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
        @cls.create_idx_abs
        def idx_fn(idxs: List[Nat]) -> T_box:
            return vec[idxs.first()]

        return Array.create(shape=Vec.create_infer(vec.length), idx_abs=idx_fn)

    @classmethod
    def create_idx_abs(
        cls, fn: typing.Callable[[List[Nat]], T_box]
    ) -> Abstraction[List[Nat], T_box]:
        return Abstraction.create(fn, List(None, Nat(None)))

    @classmethod
    def create_shape(cls, *xs: Nat) -> Vec[Nat]:
        return Vec.create_args(Nat(None), *xs)

    @classmethod
    def create_idx(cls, *xs: Nat) -> List[Nat]:
        return List.create(Nat(None), *xs)

    def __getitem__(self, idx: List[Nat]) -> T_box:
        return self.idx_abs(idx)

    def to_list(self) -> List[T_box]:
        def fn(value: List[T_box], i: Nat) -> List[T_box]:
            return value.append(self[List.create(Nat(None), i)])

        return self.shape[Nat(0)].loop(
            List.create(self.dtype),
            Abstraction.create_bin(fn, List(None, self.dtype), Nat(None)),
        )

    def to_vec(self) -> Vec[T_box]:
        return Vec.create(self.shape[Nat(0)], self.to_list())

    def to_value(self) -> T_box:
        return self[self.create_idx()]


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[List[Nat], T_box]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[1]
