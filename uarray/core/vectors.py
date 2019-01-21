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

    length: Nat = dataclasses.field(init=False)
    list: List[T_box] = dataclasses.field(init=False)

    @property
    def _concrete(self):
        return isinstance(self.value, Operation) and self.value.name == Vec

    def __post_init__(self):
        self.length = self._get_length()
        self.list = self._get_list()

    def __hash__(self):
        return hash((type(self), self.value, self.dtype))

    @classmethod
    def create(cls, length: Nat, lst: List[T_box]) -> "Vec[T_box]":
        return cls(Operation(Vec, (length, lst)), lst.dtype)

    @classmethod
    def create_args(cls, dtype: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create(Nat(len(args)), List.create(dtype, *args))

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "Vec[T_box]":
        return cls.create_args(arg._replace(None), arg, *args)

    def _get_length(self) -> Nat:
        return Nat(Operation(Vec._get_length, (self,)))

    def _get_list(self) -> List[T_box]:
        return List(Operation(Vec._get_list, (self,)), self.dtype)

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
        return self.create(self.length + Nat(1), self.list.append(item))

    def concat(self, other: "Vec[T_box]") -> "Vec[T_box]":
        return self.create(self.length + other.length, self.list.concat(other.list))

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
        return self.create(self.length, self.list.reverse())

    def reduce(
        self, initial: V_box, op: Abstraction[V_box, Abstraction[T_box, V_box]]
    ) -> V_box:
        return self.list.reduce(self.length, initial, op)


@register(ctx, Vec._get_length)
def _get_length(self: Vec[T_box]) -> Nat:
    if not self._concrete:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Vec._get_list)
def _get_list(self: Vec[T_box]) -> List[T_box]:
    if not self._concrete:
        return NotImplemented
    return self.value.args[1]
