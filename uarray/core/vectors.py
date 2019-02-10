import dataclasses
import typing

from .abstractions import *
from .context import *
from .lists import *
from .naturals import *
from ..dispatch import *

__all__ = ["Vec"]

T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


@dataclasses.dataclass
class Vec(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any = None
    dtype: T_box = typing.cast(T_box, Box(None))

    @property
    def list(self) -> List[T_box]:
        return self._get_list()

    @property
    def length(self) -> Nat:
        return self._get_length()

    @staticmethod
    @concrete_operation
    def create(length: Nat, lst: List[T_box]) -> "Vec[T_box]":
        return Vec(dtype=lst.dtype)

    @classmethod
    def create_args(cls, dtype: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create(Nat(len(args)), List.create(dtype, *args))

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create_args(arg.replace(None), arg, *args)

    @operation
    def _get_length(self) -> Nat:
        return Nat()

    @operation
    def _get_list(self) -> List[T_box]:
        return List(dtype=self.dtype)

    def with_length(self, length: Nat) -> "Vec[T_box]":
        return Vec.create(length, self.list)

    def __getitem__(self, index: Nat) -> T_box:
        return self.list[index]

    def first(self) -> T_box:
        """
        x[0]
        """
        return self.list.first()

    def rest(self) -> "Vec[T_box]":
        """
        x[1:]
        """
        return self.create(self.length - Nat(1), self.list.rest())

    def push(self, item: T_box) -> "Vec[T_box]":
        return self.create(self.length + Nat(1), self.list.push(item))

    def append(self, item: T_box) -> "Vec[T_box]":
        return self.create(self.length + Nat(1), self.list.append(self.length, item))

    def concat(self, other: "Vec[T_box]") -> "Vec[T_box]":
        return self.create(
            self.length + other.length, self.list.concat(self.length, other.list)
        )

    def drop(self, n: Nat) -> "Vec[T_box]":
        """
        x[:-n]
        """
        return self.create(self.length - n, self.list.drop(n))

    def take(self, n: Nat) -> "Vec[T_box]":
        """
        x[:n]
        """
        return self.create(n, self.list.take(n))

    def reverse(self) -> "Vec[T_box]":
        """
        x[::-1]
        """
        return self.create(self.length, self.list.reverse(self.length))

    def reduce(
        self, initial: V_box, op: Abstraction[V_box, Abstraction[T_box, V_box]]
    ) -> V_box:
        return self.list.reduce(self.length, initial, op)

    def reduce_fn(
        self, initial: V_box, op: typing.Callable[[V_box, T_box], V_box]
    ) -> V_box:
        abs_ = Abstraction.create_bin(op, initial.replace(None), self.dtype)
        return self.reduce(initial, abs_)


@register(ctx, Vec._get_length)
def _get_length(self: Vec[T_box]) -> Nat:
    if not isinstance(self.value, Operation) or not self.value.name == Vec.create:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Vec._get_list)
def _get_list(self: Vec[T_box]) -> List[T_box]:
    if not isinstance(self.value, Operation) or not self.value.name == Vec.create:
        return NotImplemented
    return self.value.args[1]
