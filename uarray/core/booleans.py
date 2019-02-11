import typing

from .context import *
from ..dispatch import *

__all__ = ["Bool"]


T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)


class Bool(Box):
    @operation
    def if_(self, if_true: T_box, if_false: T_box) -> T_box:
        return if_true

    @operation
    def and_(self, other: "Bool") -> "Bool":
        return Bool()

    @operation
    def or_(self, other: "Bool") -> "Bool":
        return Bool()

    @operation
    def not_(self) -> "Bool":
        return Bool()

    @operation
    def equal(self, other: "Bool") -> "Bool":
        return Bool()


@register(ctx, Bool.if_)
def if_(self: Bool, if_true: T_box, if_false: T_box) -> T_box:
    return if_true if extract_value(bool, self) else if_false


@register(ctx, Bool.not_)
def not_(self: Bool) -> Bool:
    return Bool(not extract_value(bool, self))


@register(ctx, Bool.and_)
def and_(self: Bool, other: Bool) -> Bool:
    return Bool(extract_value(bool, self) and extract_value(bool, other))


@register(ctx, Bool.or_)
def or_(self: Bool, other: Bool) -> Bool:
    return Bool(extract_value(bool, self) or extract_value(bool, other))


@register(ctx, Bool.equal)
def equal(self: Bool, other: Bool) -> Bool:
    return Bool(extract_value(bool, self) == extract_value(bool, other))
