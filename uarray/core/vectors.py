import typing

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


class Vec(Box[VecOperation[T_box]], typing.Generic[T_box]):
    @classmethod
    def create(cls, length: Nat, lst: List[T_box]) -> "Vec[T_box]":
        return cls(Operation(Vec, (length, lst)))

    @classmethod
    def create_args(cls, arg_type: typing.Type[T_box], *args: T_box) -> "Vec[T_box]":
        return cls.create(Nat(len(args)), List.create_args(arg_type, *args))

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create_args(type(arg), arg, *args)

    @property
    def _length(self) -> Nat:
        return self.value.args[0]

    @property
    def _list(self) -> List[T_box]:
        return self.value.args[1]

    def __getitem__(self, index: Nat) -> T_box:
        return self._list[index]

    def first(self) -> T_box:
        """
        x[0]
        """
        return self._list.first()

    def rest(self) -> "Vec[T_box]":
        """
        x[1:]
        """
        return self.create(self._length - Nat(1), self._list.rest())

    def push(self, item: T_box) -> "Vec[T_box]":
        return self.create(self._length + Nat(1), self._list.push(item))

    def concat(self, other: "Vec[T_box]") -> "Vec[T_box]":
        return self.create(self._length + other._length, self._list.concat(other._list))

    def drop(self, n: Nat) -> "Vec[T_box]":
        """
        x[:-n]
        """
        return self.create(self._length - n, self._list.drop(n))

    def take(self, n: Nat) -> "Vec[T_box]":
        """
        x[:n]
        """
        return self.create(n, self._list.take(n))

    def reverse(self) -> "Vec[T_box]":
        """
        x[::-1]
        """
        return self.create(self._length, self._list.reverse())

    def reduce(
        self, initial: V_box, op: Abstraction[V_box, Abstraction[T_box, V_box]]
    ) -> V_box:
        return self._list.reduce(self._length, initial, op)
