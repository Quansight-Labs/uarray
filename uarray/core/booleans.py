import typing

from .context import *

from ..dispatch import *

__all__ = ["Bool"]


T = typing.TypeVar("T")
T_cov = typing.TypeVar("T_cov", covariant=True)

T_box = typing.TypeVar("T_box", bound=Box)
T_wrapper = typing.TypeVar("T_wrapper", bound=Wrapper)


class Bool(Wrapper):
    def if_(self, if_true: T_wrapper, if_false: T_wrapper) -> T_wrapper:
        op = Operation(Bool.if_, [self.value, if_true.value, if_false.value])
        return type(if_true)(Box(op))

    def and_(self, other: "Bool") -> "Bool":
        op = Operation(Bool.and_, [self.value, other.value])
        return Bool(Box(op))

    def or_(self, other: "Bool") -> "Bool":
        op = Operation(Bool.or_, [self.value, other.value])
        return Bool(Box(op))

    def not_(self) -> "Bool":
        op = Operation(Bool.not_, [self.value])
        return Bool(Box(op))

    def equal(self, other: "Bool") -> "Bool":
        op = Operation(Bool.equal, [self.value, other.value])
        return Bool(Box(op))


@register(ctx, Bool.if_)
def if_(self: Box, if_true: T_box, if_false: T_box) -> T_box:
    if isinstance(self.value, bool):
        return if_true if self.value else if_false
    return NotImplemented


@register(ctx, Bool.not_)
def not_(self: Box) -> Box:
    if isinstance(self.value, bool):
        return Bool(Box(not self.value.value))
    return NotImplemented


@register(ctx, Bool.and_)
def and_(self: Bool, other: Bool) -> Bool:
    if isinstance(self.value.value, bool) and isinstance(other.value.value, bool):
        return Bool(Box(self.value.value and other.value.value))
    return NotImplemented


@register(ctx, Bool.or_)
def or_(self: Bool, other: Bool) -> Bool:
    if isinstance(self.value.value, bool) and isinstance(other.value.value, bool):
        return Bool(Box(self.value.value or other.value.value))
    return NotImplemented


@register(ctx, Bool.equal)
def equal(self: Bool, other: Bool) -> Bool:
    if isinstance(self.value.value, bool) and isinstance(other.value.value, bool):
        return Bool(Box(self.value.value == other.value.value))
    return NotImplemented
