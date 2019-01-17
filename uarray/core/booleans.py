import typing

from .context import *

from ..dispatch import *

__all__ = ["Bool"]


T = typing.TypeVar("T")
T_cov = typing.TypeVar("T_cov", covariant=True)

T_box = typing.TypeVar("T_box", bound=Box)
T_bool = typing.TypeVar("T_bool", bound="Bool")
T_wrapper = typing.TypeVar("T_wrapper", bound=Wrapper)


class Bool(Wrapper):
    def if_(self, if_true: T_wrapper, if_false: T_wrapper) -> T_wrapper:
        return type(if_true)(Box(Operation(Bool.if_, [self, if_true, if_false])))

    def and_(self: T_bool, other: T_bool) -> "Bool":
        return Bool(Box(Operation(Bool.and_, [self, other])))

    def or_(self: T_bool, other: T_bool) -> "Bool":
        return Bool(Box(Operation(Bool.or_, [self, other])))

    def not_(self: T_bool) -> "Bool":
        return Bool(Box(Operation(Bool.not_, [self])))

    def equal(self: T_bool, other: T_bool) -> "Bool":
        return Bool(Box(Operation(Bool.equal, [self, other])))


@register(ctx, Bool.if_)
def if_(self: Bool, if_true: T_wrapper, if_false: T_wrapper) -> T_wrapper:
    if isinstance(self.value.value, bool):
        return if_true if self.value else if_false
    return NotImplemented


@register(ctx, Bool.not_)
def not_(self: Bool) -> Bool:
    if isinstance(self.value.value, bool):
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
