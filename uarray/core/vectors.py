import typing
import dataclasses

from ..dispatch import *
from .context import *
from .booleans import *
from .abstractions import *
from .naturals import *
from .lists import *


__all__ = ["Vec"]

T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)

##
# Types
##

VecOperation = Operation[typing.Tuple[Nat, List[T_box]]]


@dataclasses.dataclass
class Vec(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any
    dtype: T_box

    @property
    def _concrete(self):
        return isinstance(self.value, Operation) and self.value.name == Vec

    @classmethod
    def create(cls, length: Nat, lst: List[T_box]) -> "Vec[T_box]":
        return cls(Operation(Vec, (length, lst)), lst.dtype)

    @classmethod
    def create_args(cls, dtype: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create(Nat(len(args)), List.create(dtype, *args))

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create_args(arg._replace(None), arg, *args)

    def get_length(self) -> Nat:
        return Nat(Operation(Vec.get_length, (self,)))

    def get_list(self) -> List[T_box]:
        return List(Operation(Vec.get_list, (self,)), self.dtype)

    def __getitem__(self, index: Nat) -> T_box:
        return self.get_list()[index]

    def first(self) -> T_box:
        """
        x[0]
        """
        return self.get_list().first()

    def rest(self) -> "Vec[T_box]":
        """
        x[1:]
        """
        return self.create(self.get_length() - Nat(1), self.get_list().rest())

    def push(self, item: T_box) -> "Vec[T_box]":
        return self.create(self.get_length() + Nat(1), self.get_list().push(item))

    def append(self, item: T_box) -> "Vec[T_box]":
        return self.create(self.get_length() + Nat(1), self.get_list().append(item))

    def concat(self, other: "Vec[T_box]") -> "Vec[T_box]":
        return self.create(
            self.get_length() + other.get_length(),
            self.get_list().concat(other.get_list()),
        )

    def drop(self, n: Nat) -> "Vec[T_box]":
        """
        x[:-n]
        """
        return self.create(self.get_length() - n, self.get_list().drop(n))

    def take(self, n: Nat) -> "Vec[T_box]":
        """
        x[:n]
        """
        return self.create(n, self.get_list().take(n))

    def reverse(self) -> "Vec[T_box]":
        """
        x[::-1]
        """
        return self.create(self.get_length(), self.get_list().reverse())

    def reduce(
        self, initial: V_box, op: Abstraction[V_box, Abstraction[T_box, V_box]]
    ) -> V_box:
        return self.get_list().reduce(self.get_length(), initial, op)


@register(ctx, Vec.get_length)
def get_length(self: Vec[T_box]) -> Nat:
    if not self._concrete:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Vec.get_list)
def get_list(self: Vec[T_box]) -> List[T_box]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[1]

