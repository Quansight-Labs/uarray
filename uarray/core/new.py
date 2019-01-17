import typing
import typing_extensions

from ..dispatch import *

T = typing.TypeVar("T")
V = typing.TypeVar("V")
T_cov = typing.TypeVar("T_cov", covariant=True)
T_contra = typing.TypeVar("T_contra", contravariant=True)


class AbstractionProtocol(typing_extensions.Protocol[T_contra, T_cov]):

    # @classmethod
    # def create(self, fn: )

    def apply(self, arg: T_contra) -> T_cov:
        ...


class BoolProtocol(typing_extensions.Protocol):
    def if_(self, is_true: T, is_false: T) -> T:
        ...


# abc


class NatProtocol(typing_extensions.Protocol):
    def lte(self, other: "NatProtocol") -> BoolProtocol:
        ...

    def lt(self, other: "NatProtocol") -> BoolProtocol:
        ...

    def incr(self) -> "NatProtocol":
        ...

    def decr(self) -> "NatProtocol":
        ...

    def add(self, other: "NatProtocol") -> "NatProtocol":
        ...

    def mutiply(self, other: "NatProtocol") -> "NatProtocol":
        ...

    def subtract(self, other: "NatProtocol") -> "NatProtocol":
        ...

    def equal(self, other: "NatProtocol") -> BoolProtocol:
        ...

    def loop(
        self,
        initial: T,
        op: AbstractionProtocol[T, AbstractionProtocol["NatProtocol", T]],
    ) -> "NatProtocol":
        """
        v = initial
        for i in range(n):
            v = op(v)(i)
        return v
        """
        ...


T_list = typing.TypeVar("T_list", bound="ListProtocol")


class ListProtocol(typing_extensions.Protocol[T]):
    @classmethod
    def create(cls, *items: T) -> "ListProtocol[T]":
        ...

    def getitem(self, i: NatProtocol) -> T:
        ...

    def first(self) -> T:
        ...

    def rest(self) -> "ListProtocol[T]":
        ...

    def push(self, item: T) -> "ListProtocol[T]":
        ...

    def concat(self: T_list, other: T_list) -> "ListProtocol[T]":
        ...

    def drop(self, n: NatProtocol) -> "ListProtocol[T]":
        ...

    def take(self, n: NatProtocol) -> "ListProtocol[T]":
        ...

    def reverse(self) -> "ListProtocol[T]":
        ...

    def sort(self) -> "ListProtocol[T]":
        ...

    def reduce(
        self,
        length: NatProtocol,
        initial: V,
        op: AbstractionProtocol[V, AbstractionProtocol[T, V]],
    ) -> V:
        """
        v = initial
        for i in range(length):
            v = op(v)(self.getitem(i))
        return v
        """
        ...


class TupleList(typing.Generic[T]):
    def __init__(self, node: Node[typing.Collection[T]]):
        self.node = node

    @classmethod
    def create(cls, *args: T) -> ListProtocol[T]:
        return cls(Node("tuple_list", tuple(args)))

    def getitem(self, i: IntType) -> T:
        return self.node.args[i.node.args[1]]

    def first(self) -> T:
        ...

    def rest(self) -> "TupleList[T]":
        ...

    def push(self, item: T) -> "TupleList[T]":
        ...

    def concat(self, other: "TupleList[T]") -> ListProtocol[T]:
        ...

    def drop(self, n: NatProtocol) -> "TupleList[T]":
        ...

    def take(self, n: NatProtocol) -> "TupleList[T]":
        ...

    def reverse(self) -> "TupleList[T]":
        ...

    def sort(self) -> "TupleList[T]":
        ...

    def reduce(
        self,
        length: NatProtocol,
        initial: V,
        op: AbstractionProtocol[V, AbstractionProtocol[T, V]],
    ) -> V:
        ...

