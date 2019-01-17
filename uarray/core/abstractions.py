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
W_box = typing.TypeVar("W_box", bound=Box)
X_box = typing.TypeVar("X_box", bound=Box)
T_box_cov = typing.TypeVar("T_box_cov", bound=Box, covariant=True)
T_box_contra = typing.TypeVar("T_box_contra", bound=Box, contravariant=True)

U_box_cov = typing.TypeVar("U_box_cov", bound=Box, covariant=True)
U_box_contra = typing.TypeVar("U_box_contra", bound=Box, contravariant=True)


VariableType = Box[object]


AbstractionOperation = Operation[typing.Tuple[VariableType, T_box]]

BinaryAbstraction = "Abstraction[T_box, Abstraction[U_box, V_box]]"


class Abstraction(
    Box[AbstractionOperation[T_box_cov]], typing.Generic[T_box_contra, T_box_cov]
):
    """
    Abstraction from type T_box_contra to type T_box_cov.
    """

    @classmethod
    def create(
        cls,
        fn: typing.Callable[[T_box], U_box],
        create_variable: typing.Callable[[object], T_box],
    ) -> "Abstraction[T_box, U_box]":
        variable: T_box = create_variable(None)
        return cls(Operation(Abstraction, (variable, fn(variable))))

    @classmethod
    def create_bin(
        cls,
        fn: typing.Callable[[T_box, U_box], V_box],
        create_variable_1: typing.Callable[[object], T_box],
        create_variable_2: typing.Callable[[object], U_box],
    ) -> "Abstraction[T_box, Abstraction[U_box, V_box]]":
        return cls.create(
            lambda arg1: cls.create(lambda arg2: fn(arg1, arg2), create_variable_2),
            create_variable_1,
        )

    @classmethod
    def const(cls, value: T_box) -> "Abstraction[Box, T_box]":
        return cls.create(lambda _: value, type(value))

    @classmethod
    def identity(cls, arg_type: typing.Type[T_box]) -> "Abstraction[T_box, T_box]":
        return cls.create(lambda v: v, arg_type)

    def __call__(self, arg: T_box_contra) -> T_box_cov:
        # copy so that we can replace without replacing original abstraction
        variable, body = copy.deepcopy(self.value.args)

        variable.value = arg.value
        return body

    def compose(
        self, other: "Abstraction[U_box_contra, T_box_contra]"
    ) -> "Abstraction[U_box_contra, T_box_cov]":
        """
        self.compose(other)(v) == self(other(v))
        """
        other_variable, other_body = other.value.args
        return Abstraction(other_variable, self(other_body))
