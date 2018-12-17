"""
Typed lambda calculus
"""
from ..machinery import *

__all__ = ["abstraction", "AbstractionType", "Apply", "never", "const"]
T = typing.TypeVar("T")
U = typing.TypeVar("U")


class Variable(matchpy.Operation):
    arity = matchpy.Arity(0, True)
    name = "variable"


class AbstractionType(typing.Generic[T, U]):
    pass


@operation
def Abstraction(var: T, term: U) -> AbstractionType[T, U]:
    ...


"""
Why is abstraction not just a python callable??

We don't really ever translate without evalling right?

But we kinda wanna *see* the translated version! And have it reduce
"""

_i = 0


def abstraction(
    body: typing.Callable[[T], U], var_name: str = None
) -> AbstractionType[T, U]:
    global _i
    if var_name is None:
        var_name = f"v{_i}"
        _i += 1
    var = Variable(variable_name=var_name)
    return Abstraction(var, body(var))


@operation
def Apply(f: AbstractionType[T, U], x: T) -> U:
    ...


@replacement
def _apply_abstraction(var: T, body: U, arg: T) -> DoubleThunkType[U]:
    return (
        lambda: Apply(Abstraction(var, body), arg),
        lambda: matchpy.substitute(
            body, {typing.cast(Variable, var).variable_name: arg}
        ),
    )


never: AbstractionType[typing.Any, typing.Any] = abstraction(
    lambda _: matchpy.Symbol("Never")
)


def const(x: T) -> AbstractionType[typing.Any, T]:
    return abstraction(lambda _: x)
