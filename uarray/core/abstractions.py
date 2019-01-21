"""
Lambda calculus
"""
import typing
import dataclasses

from ..dispatch import *
from .context import *
from .pairs import *

__all__ = ["Abstraction", "Variable"]

T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)
W_box = typing.TypeVar("W_box", bound=Box)
X_box = typing.TypeVar("X_box", bound=Box)

T_box_cov = typing.TypeVar("T_box_cov", bound=Box, covariant=True)
U_box_cov = typing.TypeVar("U_box_cov", bound=Box, covariant=True)

T_box_contra = typing.TypeVar("T_box_contra", bound=Box, contravariant=True)
U_box_contra = typing.TypeVar("U_box_contra", bound=Box, contravariant=True)


@dataclasses.dataclass(eq=False, frozen=True)
class Variable:
    name: typing.Optional[str] = None

    def __str__(self):
        return self.name or ""


@dataclasses.dataclass
class Abstraction(Box[typing.Any], typing.Generic[T_box_contra, T_box_cov]):
    """
    Abstraction from type T_box_contra to type T_box_cov.
    """

    value: typing.Any
    rettype: T_box_cov

    def __hash__(self):
        return hash((type(self), self.value, self.rettype))

    @property
    def _concrete(self) -> bool:
        return isinstance(self.value, Operation) and self.value.name == Abstraction

    def __call__(self, arg: T_box_contra) -> T_box_cov:
        return self.rettype._replace(Operation(Abstraction.__call__, (self, arg)))

    @classmethod
    def create(
        cls, fn: typing.Callable[[T_box], U_box], arg_type: T_box
    ) -> "Abstraction[T_box, U_box]":
        var = Variable()
        arg = arg_type._replace(var)
        body = fn(arg)
        return cls(value=Operation(Abstraction, (arg, body)), rettype=body._replace())

    @classmethod
    def create_bin(
        cls,
        fn: typing.Callable[[T_box, U_box], V_box],
        variable1: T_box,
        variable2: U_box,
    ) -> "Abstraction[T_box, Abstraction[U_box, V_box]]":
        return cls.create(
            lambda arg1: cls.create(lambda arg2: fn(arg1, arg2), variable2), variable1
        )

    @classmethod
    def const(cls, value: T_box) -> "Abstraction[Box, T_box]":
        return cls.create(lambda _: value, value._replace(object()))

    @classmethod
    def identity(cls, arg: T_box) -> "Abstraction[T_box, T_box]":
        return cls.create(lambda v: v, arg)

    def compose(
        self, other: "Abstraction[U_box_contra, T_box_contra]"
    ) -> "Abstraction[U_box_contra, T_box_cov]":
        """
        self.compose(other)(v) == self(other(v))
        """
        return self._replace(Operation(Abstraction.compose, (self, other)))


@register(ctx, Abstraction.__call__)
def __call__(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    if not self._concrete:
        return NotImplemented
    return self.rettype._replace(Operation("replace", (*self.value.args, arg)))


@register(ctx, "replace")
def replace_(
    variable: Box[Variable], body: U_box, arg: T_box
) -> typing.Union[U_box, T_box]:
    bodyval = body.value
    if variable.value is bodyval:
        return arg
    cs = children(bodyval)
    if not cs:
        return body
    return body._replace(
        dataclasses.replace(
            bodyval,
            args=tuple(
                child._replace(Operation("replace", (variable, child, arg)))
                for child in cs
            ),
        )
    )


@register(ctx, Abstraction.compose)
def compose(
    self: Abstraction[T_box_contra, T_box_cov],
    other: Abstraction[U_box_contra, T_box_contra],
) -> Abstraction[U_box_contra, T_box_cov]:
    if not self._concrete or not other._concrete:
        return NotImplemented

    other_variable, other_body = other.value.args
    return Abstraction(
        Operation(Abstraction, (other_variable, self(other_body))), self.rettype
    )
