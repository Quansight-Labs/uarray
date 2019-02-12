import typing

from .abstractions import *
from .booleans import *
from .context import *
from ..dispatch import *

__all__ = ["Natural"]

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)


class Natural(Box[typing.Any]):
    @operation
    def lte(self, other: "Natural") -> Bool:
        return Bool()

    @operation
    def lt(self, other: "Natural") -> Bool:
        return Bool()

    @operation
    def __add__(self, other: "Natural") -> "Natural":
        return Natural()

    @operation
    def __mul__(self, other: "Natural") -> "Natural":
        return Natural()

    @operation
    def __sub__(self, other: "Natural") -> "Natural":
        return Natural()

    @operation
    def __floordiv__(self, other: "Natural") -> "Natural":
        return Natural()

    @operation
    def __mod__(self, other: "Natural") -> "Natural":
        return Natural()

    @operation
    def equal(self, other: "Natural") -> "Bool":
        return Bool()

    @operation
    def loop(
        self, initial: T_box, fn: Abstraction[T_box, Abstraction["Natural", T_box]]
    ) -> T_box:
        """
        v = initial
        for i in range(n):
            v = op(v)(i)
        return v
        """
        return initial

    def loop_abstraction(
        self, initial: T_box, fn: typing.Callable[[T_box, "Natural"], T_box]
    ) -> T_box:
        return self.loop(
            initial, Abstraction.create_bin(fn, initial.replace(), Natural())
        )


@register(ctx, Natural.equal)
def equal(self: Natural, other: Natural) -> Bool:
    return Bool(extract_value(int, self) == extract_value(int, other))


@register(ctx, Natural.lte)
def lte(self: Natural, other: Natural) -> Bool:
    return Bool(extract_value(int, self) <= extract_value(int, other))


@register(ctx, Natural.lt)
def lt(self: Natural, other: Natural) -> Bool:
    return Bool(extract_value(int, self) < extract_value(int, other))


@register(ctx, Natural.__add__)
def __add__(self: Natural, other: Natural) -> Natural:
    return Natural(extract_value(int, self) + extract_value(int, other))


@register(ctx, Natural.__mul__)
def __mul__(self: Natural, other: Natural) -> Natural:
    return Natural(extract_value(int, self) * extract_value(int, other))


@register(ctx, Natural.__sub__)
def __sub__(self: Natural, other: Natural) -> Natural:
    return Natural(extract_value(int, self) - extract_value(int, other))


@register(ctx, Natural.__floordiv__)
def __floordiv__(self: Natural, other: Natural) -> Natural:
    return Natural(extract_value(int, self) // extract_value(int, other))


@register(ctx, Natural.__mod__)
def __mod__(self: Natural, other: Natural) -> Natural:
    return Natural(extract_value(int, self) % extract_value(int, other))


@register(ctx, Natural.loop)
def loop(
    self, initial: T_box, fn: Abstraction[T_box, Abstraction["Natural", T_box]]
) -> T_box:
    v = initial
    for i in range(extract_value(int, self)):
        v = fn(v)(Natural(i))
    return v


@register(ctx, Natural.__add__)
def __add__0_left(self: Natural, other: Natural) -> Natural:
    if self.value == 0:
        return other
    return NotImplemented


@register(ctx, Natural.__add__)
def __add__0_right(self: Natural, other: Natural) -> Natural:
    if other.value == 0:
        return self
    return NotImplemented


@register(ctx, Natural.__mul__)
def __mul__0_left(self: Natural, other: Natural) -> Natural:
    if self.value == 0:
        return self
    return NotImplemented


@register(ctx, Natural.__mul__)
def __mul__0_right(self: Natural, other: Natural) -> Natural:
    if other.value == 0:
        return other
    return NotImplemented

