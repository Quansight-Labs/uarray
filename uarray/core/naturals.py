import typing
import typing_extensions
import abc
import dataclasses

from ..dispatch import *
from .booleans import *
from .abstractions import *

__all__ = ["NatProtocol", "Nat"]

T = typing.TypeVar("T")
T_nat = typing.TypeVar("T_nat", bound="NatProtocol")
ctx = MapChainCallable()


class NatProtocol(typing_extensions.Protocol):
    @classmethod
    @abc.abstractmethod
    def create(cls, value: int) -> NatProtocol:
        ...

    @abc.abstractmethod
    def lte(self: T_nat, other: T_nat) -> BoolProtocol:
        ...

    @abc.abstractmethod
    def lt(self: T_nat, other: T_nat) -> BoolProtocol:
        ...

    @abc.abstractmethod
    def __add__(self: T_nat, other: T_nat) -> "NatProtocol":
        ...

    @abc.abstractmethod
    def __mul__(self: T_nat, other: T_nat) -> "NatProtocol":
        ...

    @abc.abstractmethod
    def __sub__(self: T_nat, other: T_nat) -> "NatProtocol":
        ...

    @abc.abstractmethod
    def __floordiv__(self: T_nat, other: T_nat) -> "NatProtocol":
        ...

    @abc.abstractmethod
    def __mod__(self: T_nat, other: T_nat) -> "NatProtocol":
        ...

    @abc.abstractmethod
    def equal(self: T_nat, other: T_nat) -> BoolProtocol:
        ...

    @abc.abstractmethod
    def loop(
        self,
        initial: T,
        op: AbstractionProtocol[T, AbstractionProtocol["NatProtocol", T]],
    ) -> T:
        """
        v = initial
        for i in range(n):
            v = op(v)(i)
        return v
        """
        ...


x: typing.Callable = NatProtocol.__add__
# xt = type(x)


@dataclasses.dataclass
class Nat(NatProtocol):
    value: int

    @classmethod
    def create(cls, value: int) -> Nat:
        return cls(value)

    def equal(self, other: Nat) -> BoolProtocol:
        return Bool.create(self.value == other.value)

    def lte(self, other: Nat) -> BoolProtocol:
        return Bool.create(self.value <= other.value)

    def lt(self, other: Nat) -> BoolProtocol:
        return Bool.create(self.value < other.value)

    def __add__(self, other: Nat) -> "NatProtocol":
        return Nat.create(self.value + other.value)

    def __mul__(self, other: Nat) -> "NatProtocol":
        return Nat.create(self.value * other.value)

    def __sub__(self, other: Nat) -> "NatProtocol":
        return Nat.create(self.value - other.value)

    def __floordiv__(self, other: Nat) -> "NatProtocol":
        return Nat.create(self.value // other.value)

    def __mod__(self, other: Nat) -> "NatProtocol":
        return Nat.create(self.value % other.value)

    def loop(
        self,
        initial: T,
        op: AbstractionProtocol[T, AbstractionProtocol["NatProtocol", T]],
    ) -> T:
        v = initial
        for i in range(self.value):
            v = op(v)(Nat.create(i))
        return v


@register(ctx, NatProtocol.__add__)
def add_0_left(left: NatProtocol, right: NatProtocol) -> NatProtocol:
    if isinstance(left, Nat) and left.value == 0:
        return right
    return NotImplemented


@register(ctx, NatProtocol.__add__)
def add_0_right(left: NatProtocol, right: NatProtocol) -> NatProtocol:
    if isinstance(right, Nat) and right.value == 0:
        return left
    return NotImplemented


@register(ctx, NatProtocol.__mul__)
def mul_0_left(left: NatProtocol, right: NatProtocol) -> NatProtocol:
    if isinstance(left, Nat) and left.value == 0:
        return right
    return NotImplemented


@register(ctx, NatProtocol.__mul__)
def mul_0_right(left: NatProtocol, right: NatProtocol) -> NatProtocol:
    if isinstance(right, Nat) and right.value == 0:
        return left
    return NotImplemented
