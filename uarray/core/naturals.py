import typing

from .abstractions import *
from .booleans import *
from .context import *
from ..dispatch import *

__all__ = ["Nat"]

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)


class Nat(Box[typing.Any]):
    @operation
    def lte(self, other: "Nat") -> Bool:
        return Bool()

    @operation
    def lt(self, other: "Nat") -> Bool:
        return Bool()

    @operation
    def __add__(self, other: "Nat") -> "Nat":
        return Nat()

    @operation
    def __mul__(self, other: "Nat") -> "Nat":
        return Nat()

    @operation
    def __sub__(self, other: "Nat") -> "Nat":
        return Nat()

    @operation
    def __floordiv__(self, other: "Nat") -> "Nat":
        return Nat()

    @operation
    def __mod__(self, other: "Nat") -> "Nat":
        return Nat()

    @operation
    def equal(self, other: "Nat") -> "Bool":
        return Bool()

    @operation
    def loop(
        self, initial: T_box, fn: Abstraction[T_box, Abstraction["Nat", T_box]]
    ) -> T_box:
        """
        v = initial
        for i in range(n):
            v = op(v)(i)
        return v
        """
        return initial


@register(ctx, Nat.equal)
def equal(self: Nat, other: Nat) -> Bool:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Bool(self.value == other.value)
    return NotImplemented


@register(ctx, Nat.lte)
def lte(self: Nat, other: Nat) -> Bool:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Bool(self.value <= other.value)
    return NotImplemented


@register(ctx, Nat.lt)
def lt(self: Nat, other: Nat) -> Bool:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Bool(self.value < other.value)
    return NotImplemented


@register(ctx, Nat.__add__)
def __add__(self: Nat, other: Nat) -> Nat:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Nat(self.value + other.value)
    return NotImplemented


@register(ctx, Nat.__mul__)
def __mul__(self: Nat, other: Nat) -> Nat:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Nat(self.value * other.value)
    return NotImplemented


@register(ctx, Nat.__sub__)
def __sub__(self: Nat, other: Nat) -> Nat:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Nat(self.value - other.value)
    return NotImplemented


@register(ctx, Nat.__floordiv__)
def __floordiv__(self: Nat, other: Nat) -> Nat:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Nat(self.value // other.value)
    return NotImplemented


@register(ctx, Nat.__mod__)
def __mod__(self: Nat, other: Nat) -> Nat:
    if isinstance(self.value, int) and isinstance(other.value, int):
        return Nat(self.value % other.value)
    return NotImplemented


@register(ctx, Nat.loop)
def loop(
    self, initial: T_box, fn: Abstraction[T_box, Abstraction["Nat", T_box]]
) -> T_box:
    if isinstance(self.value, int):
        v = initial
        for i in range(self.value):
            v = fn(v)(Nat(i))
        return v
    return NotImplemented


@register(ctx, Nat.__add__)
def __add__0_left(self: Nat, other: Nat) -> Nat:
    if self.value == 0:
        return other
    return NotImplemented


@register(ctx, Nat.__add__)
def __add__0_right(self: Nat, other: Nat) -> Nat:
    if other.value == 0:
        return self
    return NotImplemented


@register(ctx, Nat.__add__)
def __mul__0_left(self: Nat, other: Nat) -> Nat:
    if self.value == 0:
        return self
    return NotImplemented


@register(ctx, Nat.__add__)
def __mul__0_right(self: Nat, other: Nat) -> Nat:
    if other.value == 0:
        return other
    return NotImplemented


@register(ctx, Nat.__sub__)
def __sub__add(self: Nat, other: Nat) -> Nat:
    if (
        not isinstance(self.value, Operation)
        or self.value.name != Nat.__add__
        or not isinstance(other.value, int)
        or not isinstance(self.value.args[0].value, int)
    ):
        return NotImplemented
    self_l, self_r = self.value.args
    return (self_l - other) + self_r
