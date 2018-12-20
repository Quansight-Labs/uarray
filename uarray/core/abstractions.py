"""
Typed lambda calculus
"""
import typing
import matchpy

from ..machinery import *
from .pairs import *
from .equality import *
from .booleans import *

__all__ = ["Apply", "abstraction", "variable", "never_abstraction", "const_abstraction"]
T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")


##
# Constructors
##


class Variable(matchpy.Operation):
    arity = matchpy.Arity(0, True)


@operation
def Bottom():
    """
    Value that should never be returned by a function.
    (for example the getitem function for an empty list should return this type)

    https://en.wikipedia.org/wiki/Bottom_type
    """
    ...


##
# Operations
##


@replacement
def _bottom_never_equal(x):
    return lambda: Equal(Bottom(), x), lambda: bool_(False)


@replacement
def _bottom_never_equal_2(x):
    return lambda: Equal(x, Bottom()), lambda: bool_(False)


@operation
def Apply(f: PairType[T, U], x: T) -> U:
    ...


@replacement
def _apply_abstraction(var: T, body: U, arg: T) -> DoubleThunkType[U]:
    return (
        lambda: Apply(Pair(var, body), arg),
        lambda: matchpy.substitute(  # type: ignore
            body, {typing.cast(Variable, var).variable_name: arg}
        ),
    )


##
# Helpers
##


def variable(name: str) -> typing.Any:
    return Variable(variable_name=name)


_i = 0


def abstraction(body: typing.Callable[[T], U], var_name: str = None) -> PairType[T, U]:
    global _i
    if var_name is None:
        var_name = f"v{_i}"
        _i += 1
    var = typing.cast(T, variable(var_name))
    return Pair(var, body(var))


never_abstraction: PairType[typing.Any, typing.Any] = abstraction(lambda _: Bottom())


def const_abstraction(x: T) -> PairType[typing.Any, T]:
    return abstraction(lambda _: x)
