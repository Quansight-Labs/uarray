import dataclasses
import typing

from .context import *
from ..dispatch import *

__all__ = ["Pair"]

T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)


@dataclasses.dataclass
class Pair(Box[typing.Any], typing.Generic[T_box, U_box]):
    value: typing.Any = None
    left_type: T_box = typing.cast(T_box, Box())
    right_type: U_box = typing.cast(U_box, Box())

    @staticmethod
    @concrete_operation
    def create(left: T_box, right: U_box) -> "Pair[T_box, U_box]":
        return Pair(left_type=left.replace(), right_type=right.replace())

    @property
    def left(self) -> T_box:
        return self._get_left()

    @property
    def right(self) -> U_box:
        return self._get_right()

    @operation
    def _get_left(self) -> T_box:
        return self.left_type

    @operation
    def _get_right(self) -> U_box:
        return self.right_type


@register(ctx, Pair._get_left)
def _get_left(self: Pair[T_box, typing.Any]) -> T_box:
    left, right = extract_args(Pair.create, self)  # type: ignore
    return left


@register(ctx, Pair._get_right)
def _get_right(self: Pair[typing.Any, T_box]) -> T_box:
    left, right = extract_args(Pair.create, self)  # type: ignore
    return right
