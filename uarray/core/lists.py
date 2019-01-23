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

    def __hash__(self):
        # print("hashing", self.value, self.dtype)
        return hash((List, self.value, self.dtype))

    @property
    def _concrete(self) -> bool:
        return isinstance(self.value, Operation) and self.value.name == List

    @property
    def _concrete_abs(self) -> bool:
        return isinstance(self.value, Operation) and self.value.name == List.from_abs

    @property
    def _args(self) -> typing.Tuple[T_box, ...]:
        return self.value.args

    @classmethod
    def create(cls, dtype: T_box, *args: T_box) -> "List[T_box]":
        return cls(Operation(List, args), dtype)

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "List[T_box]":
        return cls.create(arg._replace(None), arg, *args)

    @classmethod
    def from_abs(cls, a: Abstraction[Nat, T_box]) -> "List[T_box]":
        return cls(Operation(List.from_abs, (a,)), a.rettype)

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
        Drops the first n items from the list.

        x[n:]
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

    def reduce_fn(
        self, length: Nat, initial: V_box, op: typing.Callable[[V_box, V_box], V_box]
    ) -> V_box:
        abs_: Abstraction[V_box, Abstraction[V_box, V_box]] = Abstraction.create_bin(
            op, initial._replace(None), initial._replace(None)
        )
        return self.reduce(length, initial, abs_)


@register(ctx, List.__getitem__)
def __getitem__(self: List[T_box], index: Nat) -> T_box:
    if not self._concrete or not index._concrete:
        return NotImplemented

    return self._args[index.value]


@register(ctx, List.__getitem__)
def __getitem___abs(self: List[T_box], index: Nat) -> T_box:
    if not self._concrete_abs:
        return NotImplemented

    return self.value.args[0](index)


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


@register(ctx, List.concat)
def concat_empty_left(self: List[T_box], other: List[T_box]) -> List[T_box]:
    if not self._concrete or self.value.args:
        return NotImplemented
    return other


@register(ctx, List.concat)
def concat_empty_right(self: List[T_box], other: List[T_box]) -> List[T_box]:
    if not other._concrete or other.value.args:
        return NotImplemented
    return self


@register(ctx, List.drop)
def drop(self: List[T_box], n: Nat) -> List[T_box]:
    if not self._concrete or not n._concrete:
        return NotImplemented
    return self._replace_args(*self._args[n.value :])


@register(ctx, List.drop)
def drop_abs(self: List[T_box], n: Nat) -> List[T_box]:
    if not isinstance(self.value, Operation) or self.value.name != List.from_abs:
        return NotImplemented

    old_abs = self.value.args[0]

    def new_list(idx: Nat) -> T_box:
        return old_abs(idx + n)

    return List.from_abs(Abstraction.create(new_list, old_abs.rettype))


@register(ctx, List.drop)
def drop_zero(self: List[T_box], n: Nat) -> List[T_box]:
    if n.value != 0:
        return NotImplemented
    return self


@register(ctx, List.take)
def take(self: List[T_box], n: Nat) -> List[T_box]:
    if not self._concrete or not n._concrete:
        return NotImplemented
    return self._replace_args(*self._args[: n.value])


@register(ctx, List.take)
def take_abs(self: List[T_box], n: Nat) -> List[T_box]:
    if not isinstance(self.value, Operation) or self.value.name != List.from_abs:
        return NotImplemented

    return self


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
