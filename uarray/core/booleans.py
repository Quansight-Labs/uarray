import typing

from .context import *
from ..dispatch import *

__all__ = ["Bool"]


T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)


class Bool(Box):
    def if_(self, if_true: T_box, if_false: T_box) -> T_box:
        op = Operation(Bool.if_, (self, if_true, if_false))
        return if_true.replace(op)

    def and_(self, other: "Bool") -> "Bool":
        op = Operation(Bool.and_, (self, other))
        return Bool(op)

    def or_(self, other: "Bool") -> "Bool":
        op = Operation(Bool.or_, (self, other))
        return Bool(op)

    def not_(self) -> "Bool":
        op = Operation(Bool.not_, (self,))
        return Bool(op)

    def equal(self, other: "Bool") -> "Bool":
        op = Operation(Bool.equal, (self, other))
        return Bool(op)


@register(ctx, Bool.if_)
def if_(self: Bool, if_true: T_box, if_false: T_box) -> T_box:
    if isinstance(self.value, bool):
        return if_true if self.value else if_false
    return NotImplemented


@register(ctx, Bool.not_)
def not_(self: Bool) -> Bool:
    if isinstance(self.value, bool):
        return Bool(not self.value)
    return NotImplemented


@register(ctx, Bool.and_)
def and_(self: Bool, other: Bool) -> Bool:
    if isinstance(self.value, bool) and isinstance(other.value, bool):
        return Bool(self.value and other.value)
    return NotImplemented


@register(ctx, Bool.or_)
def or_(self: Bool, other: Bool) -> Bool:
    if isinstance(self.value, bool) and isinstance(other.value, bool):
        return Bool(self.value or other.value)
    return NotImplemented


@register(ctx, Bool.equal)
def equal(self: Bool, other: Bool) -> Bool:
    if isinstance(self.value, bool) and isinstance(other.value, bool):
        return Bool(self.value == other.value)
    return NotImplemented
