import typing
import dataclasses

from ..dispatch import *
from .abstractions import *
from .booleans import *
from .context import *
from .naturals import *

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


__all__ = ["List"]


@dataclasses.dataclass
class List(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any
    dtype: T_box

    @property
    def _concrete(self) -> bool:
        return isinstance(self.value, Operation) and self.value.name == List

    @property
    def _args(self) -> typing.Tuple[T_box, ...]:
        return self.value.args

    @classmethod
    def create(cls, dtype: T_box, *args: T_box) -> "List[T_box]":
        return cls(Operation(List, args), dtype)

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "List[T_box]":
        return cls.create(arg._replace(None), arg, *args)

    def _replace_args(self, *args: T_box) -> "List[T_box]":
        return self._replace(Operation(List, args))

    def __getitem__(self, index: Nat) -> T_box:
        op = Operation(List.__getitem__, (self, index))
        return self.dtype._replace(op)

    # TODO: Refactor many of these to __getitem__ slices

    def first(self) -> T_box:
        """
        x[0]
        """
        return self.dtype._replace(Operation(List.first, (self,)))

    def rest(self) -> "List[T_box]":
        """
        x[1:]
        """
        return self._replace(Operation(List.rest, (self,)))

    def push(self, item: T_box) -> "List[T_box]":
        return self._replace(Operation(List.push, (self, item)))

    def append(self, item: T_box) -> "List[T_box]":
        return self._replace(Operation(List.append, (self, item)))

    def concat(self, other: "List[T_box]") -> "List[T_box]":
        return self._replace(Operation(List.concat, (self, other)))

    def drop(self, n: Nat) -> "List[T_box]":
        """
        x[:-n]
        """
        return self._replace(Operation(List.drop, (self, n)))

    def take(self, n: Nat) -> "List[T_box]":
        """
        x[:n]
        """
        return self._replace(Operation(List.take, (self, n)))

    def reverse(self) -> "List[T_box]":
        """
        x[::-1]
        """
        return self._replace(Operation(List.reverse, (self,)))

    def reduce(
        self,
        length: Nat,
        initial: V_box,
        op: Abstraction[V_box, Abstraction[T_box, V_box]],
    ) -> V_box:
        return initial._replace(Operation(List.reduce, (self, length, initial, op)))


@register(ctx, List.__getitem__)
def __getitem__(self: List[T_box], index: Nat) -> T_box:
    if not self._concrete or not index._concrete:
        return NotImplemented

    return self._args[index.value]


@register(ctx, List.rest)
def rest(self: List[T_box]) -> List[T_box]:
    if not self._concrete:
        return NotImplemented
    return self._replace_args(*self._args[1:])


@register(ctx, List.push)
def push(self: List[T_box], item: T_box) -> List[T_box]:
    if not self._concrete:
        return NotImplemented
    return self._replace_args(item, *self._args)


@register(ctx, List.append)
def append(self: List[T_box], item: T_box) -> List[T_box]:
    if not self._concrete:
        return NotImplemented
    return self._replace_args(*self._args, item)


@register(ctx, List.concat)
def concat(self: List[T_box], other: List[T_box]) -> List[T_box]:
    if not self._concrete or not other._concrete:
        return NotImplemented
    return self._replace_args(*self._args, *other._args)


@register(ctx, List.drop)
def drop(self: List[T_box], n: Nat) -> List[T_box]:
    if not self._concrete or not n._concrete:
        return NotImplemented
    return self._replace_args(*self._args[: len(self._args) - n.value])


@register(ctx, List.take)
def take(self: List[T_box], n: Nat) -> List[T_box]:
    if not self._concrete or not n._concrete:
        return NotImplemented
    return self._replace_args(*self._args[: n.value])


@register(ctx, List.reverse)
def reverse(self: List[T_box]) -> List[T_box]:
    if not self._concrete:
        return NotImplemented
    return self._replace_args(*self._args[::-1])


@register(ctx, List.first)
def first(self: List[T_box]) -> T_box:
    if not self._concrete:
        return NotImplemented
    return self._args[0]


@register(ctx, List.reduce)
def reduce(
    self: List[T_box],
    length: Nat,
    initial: V_box,
    op: Abstraction[V_box, Abstraction[T_box, V_box]],
) -> V_box:
    def fn(v: V_box, idx: Nat) -> V_box:
        return op(v)(self[idx])

    abstraction = Abstraction.create_bin(fn, initial._replace(None), Nat(None))
    return length.loop(initial, abstraction)
