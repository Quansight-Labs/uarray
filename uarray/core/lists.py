import typing
import typing_extensions
import abc
import dataclasses

from ..dispatch import *
from .naturals import *
from .abstractions import *

T = typing.TypeVar("T")
V = typing.TypeVar("V")
T_list = typing.TypeVar("T_list", bound="ListProtocol")
T_nat = typing.TypeVar("T_nat", bound=NatProtocol)


class ListProtocol(typing_extensions.Protocol[T]):
    @abc.abstractmethod
    @classmethod
    def create(cls, *items: T) -> "ListProtocol[T]":
        ...

    @abc.abstractmethod
    def __getitem__(self, index: T_nat) -> T:
        ...

    # TODO: Refactor many of these to __getitem__ slices

    @abc.abstractmethod
    def first(self) -> T:
        """
        x[0]
        """
        ...

    @abc.abstractmethod
    def rest(self) -> "ListProtocol[T]":
        """
        x[1:]
        """
        ...

    @abc.abstractmethod
    def push(self, item: T) -> "ListProtocol[T]":
        ...

    @abc.abstractmethod
    def concat(self: T_list, other: T_list) -> "ListProtocol[T]":
        ...

    @abc.abstractmethod
    def drop(self, n: NatProtocol) -> "ListProtocol[T]":
        """
        x[:-n]
        """
        ...

    @abc.abstractmethod
    def take(self, n: NatProtocol) -> "ListProtocol[T]":
        """
        x[:n]
        """
        ...

    @abc.abstractmethod
    def reverse(self) -> "ListProtocol[T]":
        """
        x[::-1]
        """
        ...

    def reduce(
        self,
        length: NatProtocol,
        initial: V,
        op: AbstractionProtocol[V, AbstractionProtocol[T, V]],
    ) -> V:
        @Abstraction.create_bin
        def loop_op(v: V, idx: NatProtocol) -> V:
            return op(v)(self[idx])

        return length.loop(initial, loop_op)


@dataclasses.dataclass
class List(ListProtocol[T]):
    value: typing.Sequence[T]

    @classmethod
    def create(cls, *items: T) -> "ListProtocol[T]":
        return cls(items)

    def __getitem__(self, index: Nat) -> T:
        return self.value[index.value]

    # TODO: Refactor many of these to __getitem__ slices

    def first(self) -> T:
        """
        x[0]
        """
        ...

    def rest(self) -> "ListProtocol[T]":
        """
        x[1:]
        """
        ...

    def push(self, item: T) -> "ListProtocol[T]":
        ...

    def concat(self: T_list, other: T_list) -> "ListProtocol[T]":
        ...

    def drop(self, n: NatProtocol) -> "ListProtocol[T]":
        """
        x[:-n]
        """
        ...

    def take(self, n: NatProtocol) -> "ListProtocol[T]":
        """
        x[:n]
        """
        ...

    def reverse(self) -> "ListProtocol[T]":
        """
        x[::-1]
        """
        ...

    def reduce(
        self,
        length: NatProtocol,
        initial: V,
        op: AbstractionProtocol[V, AbstractionProtocol[T, V]],
    ) -> V:
        def loop_op(v: V, idx: NatProtocol) -> V:
            return op(v)(self[idx])

        return length.loop(initial, Abstraction.create(loop_op))
