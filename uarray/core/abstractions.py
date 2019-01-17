"""
Lambda calculus
"""
import typing
import copy

from ..dispatch import *
from .context import *

__all__ = ["Abstraction"]

T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)
VariableType = Box[object]


AbstractionOperation = Operation[typing.Tuple[VariableType, T_box]]

BinaryAbstraction = "Abstraction[T_box, Abstraction[U_box, V_box]]"


class Abstraction(Box[AbstractionOperation[U_box]], typing.Generic[T_box, U_box]):
    """
    Abstraction from type T_box to type U_box.
    """

    def __call__(self, arg: T_box) -> U_box:
        variable, body = self.value.args
        op = Operation(Abstraction.__call__, (self, arg))
        return type(body)(op)

    @classmethod
    def create(
        cls,
        fn: typing.Callable[[T_box], U_box],
        create_arg: typing.Callable[[object], T_box],
    ) -> "Abstraction[T_box, U_box]":
        variable: T_box = create_arg(None)
        return cls(Operation(Abstraction, (variable, fn(variable))))

    @classmethod
    def create_bin(
        cls,
        fn: typing.Callable[[T_box, U_box], V_box],
        create_arg1: typing.Callable[[object], T_box],
        create_arg2: typing.Callable[[object], U_box],
    ) -> "Abstraction[T_box, Abstraction[U_box, V_box]]":
        return cls.create(
            lambda arg1: cls.create(lambda arg2: fn(arg1, arg2), create_arg2),
            create_arg1,
        )

    @classmethod
    def const(cls, value: T_box) -> "Abstraction[Box[object], T_box]":
        return cls.create(lambda _: value, type(value))

    @classmethod
    def identity(cls, arg_type: typing.Type[T_box]) -> "Abstraction[T_box, T_box]":
        return cls.create(lambda v: v, arg_type)


@register(ctx, Abstraction.__call__)
def apply_abstraction(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    # copy so that we can replace without replacing original abstraction
    variable, body = copy.deepcopy(self.value.args)
    # TODO: need mapping from arg to value to use...
    variable.value = arg.value
    return body
