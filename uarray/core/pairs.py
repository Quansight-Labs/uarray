import typing

from ..dispatch import *
from .context import *


T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
T_box_cov = typing.TypeVar("T_box_cov", bound=Box, covariant=True)
U_box_cov = typing.TypeVar("U_box_cov", bound=Box, covariant=True)

__all__ = ["Pair"]


class Pair(Box):
    @classmethod
    def create(cls, left: Box, right: Box) -> "Pair":
        return cls(Operation(Pair, (left, right)))

    @property
    def _concrete(self):
        return isinstance(self.value, Operation) and self.value.type == Pair

    @property
    def left(self) -> Box:
        return Box(Operation(Pair.left, (self,)))

    @property
    def right(self) -> Box:
        return Box(Operation(Pair.right, (self,)))


@register(ctx, Pair.left)
def left(self: Pair) -> Box:
    if not self._concrete:
        return NotImplemented
    return self.value.args[0]


@register(ctx, Pair.right)
def right(self: Pair) -> Box:
    if not self._concrete:
        return NotImplemented
    return self.value.args[1]
