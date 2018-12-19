"""
Typed lambda calculus
"""
import typing
import matchpy

from ..machinery import *
from .pairs import *

__all__ = ["Apply", "abstraction", "never_abstraction", "const_abstraction"]
T = typing.TypeVar("T")
U = typing.TypeVar("U")


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

_i = 0


def abstraction(body: typing.Callable[[T], U], var_name: str = None) -> PairType[T, U]:
    global _i
    if var_name is None:
        var_name = f"v{_i}"
        _i += 1
    var = typing.cast(T, Variable(variable_name=var_name))
    return Pair(var, body(var))


never_abstraction: PairType[typing.Any, typing.Any] = abstraction(lambda _: Bottom())


def const_abstraction(x: T) -> PairType[typing.Any, T]:
    return abstraction(lambda _: x)
