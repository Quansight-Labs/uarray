import typing

from ..dispatch import *
from .context import *
from .booleans import *
from .abstractions import *
from .naturals import *

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


__all__ = ["List", "ListContents", "ListType"]


class ListType(Box[typing.Type[T_box]], typing.Generic[T_box]):
    pass


class ListContents(Box):
    @classmethod
    def create(cls, *args: Box) -> "ListContents":
        return cls(Operation(ListContents, args))

    @property
    def _args(self) -> tuple:
        return self.value.args

    @property
    def _concrete(self) -> bool:
        return isinstance(self.value, Operation) and self.value.name == ListContents

    def rest(self) -> "ListContents":
        return ListContents(Operation(ListContents.rest, (self,)))

    def push(self, item: Box) -> "ListContents":
        return ListContents(Operation(ListContents.push, (self, item)))

    def concat(self, other: "ListContents") -> "ListContents":
        return ListContents(Operation(ListContents.concat, (self, other)))

    def drop(self, n: Nat) -> "ListContents":
        return ListContents(Operation(ListContents.drop, (self, n)))

    def take(self, n: Nat) -> "ListContents":
        return ListContents(Operation(ListContents.take, (self, n)))

    def reverse(self) -> "ListContents":
        return ListContents(Operation(ListContents.reverse, (self,)))


ListOperation = Operation[typing.Tuple[ListType[T_box], ListContents]]


class List(Box[ListOperation[T_box]], typing.Generic[T_box]):
    """
    Typed version of ListContents
    """

    @classmethod
    def create(
        cls, arg_type: typing.Type[T_box], contents: ListContents
    ) -> "List[T_box]":
        return List(Operation(List, (ListType(arg_type), contents)))

    @classmethod
    def create_args(cls, arg_type: typing.Type[T_box], *args: T_box) -> "List[T_box]":
        return cls.create(arg_type, ListContents.create(*args))

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "List[T_box]":
        return cls.create_args(type(arg), arg, *args)

    @property
    def _dtype(self) -> typing.Type[T_box]:
        return self.value.args[0].value

    @property
    def _contents(self) -> ListContents:
        return self.value.args[1]

    def _replace_contents(self, new_contents: ListContents) -> "List[T_box]":
        return List(Operation(List, (self.value.args[0], new_contents)))

    def __getitem__(self, index: Nat) -> T_box:
        return self._dtype(Operation(List.__getitem__, (self, index)))

    # TODO: Refactor many of these to __getitem__ slices

    def first(self) -> T_box:
        """
        x[0]
        """
        return self._dtype(Operation(List.first, (self,)))

    def rest(self) -> "List[T_box]":
        """
        x[1:]
        """
        return self._replace_contents(self._contents.rest())

    def push(self, item: T_box) -> "List[T_box]":
        return self._replace_contents(self._contents.push(item))

    def concat(self, other: "List[T_box]") -> "List[T_box]":
        return self._replace_contents(self._contents.concat(other._contents))

    def drop(self, n: Nat) -> "List[T_box]":
        """
        x[:-n]
        """
        return self._replace_contents(self._contents.drop(n))

    def take(self, n: Nat) -> "List[T_box]":
        """
        x[:n]
        """
        return self._replace_contents(self._contents.drop(n))

    def reverse(self) -> "List[T_box]":
        """
        x[::-1]
        """
        return self._replace_contents(self._contents.reverse())

    def reduce(
        self,
        length: Nat,
        initial: V_box,
        op: Abstraction[V_box, Abstraction[T_box, V_box]],
    ) -> V_box:
        return type(initial)(Operation(List.reduce, (self, length, initial, op)))


@register(ctx, List.__getitem__)
def __getitem__(self: List[T_box], index: Nat) -> T_box:
    if not self._contents._concrete or not index._concrete:
        return NotImplemented

    return self._contents._args[index.value]


@register(ctx, ListContents.rest)
def rest(self: ListContents) -> ListContents:
    if not self._concrete:
        return NotImplemented
    return ListContents.create(*self._args[1:])


@register(ctx, ListContents.push)
def push(self: ListContents, item: Box) -> ListContents:
    if not self._concrete:
        return NotImplemented
    return ListContents.create(item, *self._args)


@register(ctx, ListContents.concat)
def concat(self: ListContents, other: ListContents) -> ListContents:
    if not self._concrete or not other._concrete:
        return NotImplemented
    return ListContents.create(*self._args, *other._args)


@register(ctx, ListContents.drop)
def drop(self: ListContents, n: Nat) -> ListContents:
    if not self._concrete or not n._concrete:
        return NotImplemented
    return ListContents.create(*self._args[: -n.value])


@register(ctx, ListContents.take)
def take(self: ListContents, n: Nat) -> ListContents:
    if not self._concrete or not n._concrete:
        return NotImplemented
    return ListContents.create(*self.value[: n.value])


@register(ctx, ListContents.reverse)
def reverse(self: ListContents) -> ListContents:
    if not self._concrete:
        return NotImplemented
    return ListContents.create(*self.value[::-1])


@register(ctx, List.first)
def first(self: List[T_box]) -> T_box:
    if not self._contents._concrete:
        return NotImplemented
    return self._contents._args[0]


@register(ctx, List.reduce)
def reduce(
    self: List[T_box],
    length: Nat,
    initial: V_box,
    op: Abstraction[V_box, Abstraction[T_box, V_box]],
) -> V_box:
    def fn(v: V_box, idx: Nat) -> V_box:
        return op(v)(self[idx])

    abstraction = Abstraction.create_bin(fn, type(initial), Nat)
    return length.loop(initial, abstraction)
