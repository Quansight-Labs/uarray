import typing

from ..dispatch import *
from .context import *
from .booleans import *
from .abstractions import *

__all__ = ["Nat"]

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)


class Nat(Box[typing.Any]):
    def lte(self, other: "Nat") -> Bool:
        op = Operation(Nat.lte, (self, other))
        return Bool(op)

    def lt(self, other: "Nat") -> Bool:
        op = Operation(Nat.lt, (self, other))
        return Bool(op)

    def __add__(self, other: "Nat") -> "Nat":
        op = Operation(Nat.__add__, (self, other))
        return Nat(op)

    def __mul__(self, other: "Nat") -> "Nat":
        op = Operation(Nat.__mul__, (self, other))
        return Nat(op)

    def __sub__(self, other: "Nat") -> "Nat":
        op = Operation(Nat.__sub__, (self, other))
        return Nat(op)

    def __floordiv__(self, other: "Nat") -> "Nat":
        op = Operation(Nat.__floordiv__, (self, other))
        return Nat(op)

    def __mod__(self, other: "Nat") -> "Nat":
        op = Operation(Nat.__mod__, (self, other))
        return Nat(op)

    def equal(self, other: "Nat") -> "Bool":
        op = Operation(Nat.equal, (self, other))
        return Bool(op)

    def loop(
        self, initial: T_box, fn: Abstraction[T_box, Abstraction["Nat", T_box]]
    ) -> T_box:
        """
        v = initial
        for i in range(n):
            v = op(v)(i)
        return v
        """
        op = Operation(Nat.loop, (self, initial, fn))
        return initial.replace(op)


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
