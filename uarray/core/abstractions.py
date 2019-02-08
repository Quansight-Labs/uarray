"""
Lambda calculus
"""
import typing
import dataclasses
import functools
from ..dispatch import *
from .context import *

__all__ = ["Abstraction", "Variable", "rename_variables", "Partial"]

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)
W_box = typing.TypeVar("W_box", bound=Box)
X_box = typing.TypeVar("X_box", bound=Box)

T_box_cov = typing.TypeVar("T_box_cov", bound=Box, covariant=True)
U_box_cov = typing.TypeVar("U_box_cov", bound=Box, covariant=True)

T_box_contra = typing.TypeVar("T_box_contra", bound=Box, contravariant=True)
U_box_contra = typing.TypeVar("U_box_contra", bound=Box, contravariant=True)


@dataclasses.dataclass(frozen=True)
class Partial(typing.Generic[T]):
    """
    Simple partial function application.

    We use this over functools.partial b/c it doesn't support
    equality (https://bugs.python.org/issue3564) and we use that in testing.
    """

    fn: typing.Callable[..., T]
    args: typing.Tuple

    def __call__(self, *args) -> T:
        return self.fn(*self.args, *args)  # type: ignore


@dataclasses.dataclass(eq=False, frozen=True)
class Variable:
    name: typing.Optional[str] = None

    def __str__(self):
        return self.name or ""


@concrete.register
def variable_concrete(v: Variable):
    return False


# Why do we have data as seperate type here?
# Can't they just be functions?
# That would make type signature on replacements of them easier...


@dataclasses.dataclass
class AbstractionData(Data, typing.Generic[T_box_cov]):
    variable: Box[Variable]
    body: T_box_cov


@dataclasses.dataclass
class ConstAbstractionData(Data, typing.Generic[T_box_cov]):
    value: T_box_cov


@dataclasses.dataclass(frozen=True)
class NativeAbstractionData(typing.Generic[T_box_cov]):
    fn: typing.Callable[[T_box], U_box]
    can_call: typing.Callable[[T_box], bool]


@dataclasses.dataclass
class Abstraction(Box[typing.Any], typing.Generic[T_box_contra, T_box_cov]):
    """
    Abstraction from type T_box_contra to type T_box_cov.
    """

    value: typing.Any
    rettype: T_box_cov

    def __call__(self, arg: T_box_contra) -> T_box_cov:
        return self.rettype._replace(Operation(Abstraction.__call__, (self, arg)))

    @classmethod
    def from_variable(cls, variable: T_box, body: U_box) -> "Abstraction[T_box, U_box]":
        return cls(AbstractionData(variable, body), rettype=body._replace())

    @classmethod
    def from_variables(cls, body: Box, *variables: Box) -> "Box":
        for v in variables:
            body = cls.from_variable(v, body)
        return body

    @classmethod
    def create(
        cls, fn: typing.Callable[[T_box], U_box], arg_type: T_box, vname: str = None
    ) -> "Abstraction[T_box, U_box]":
        arg = arg_type._replace(Variable(vname))
        body = fn(arg)
        return cls.from_variable(arg, body)

    @classmethod
    def create_nary(
        cls, fn: typing.Callable[..., T_box], vnames: typing.List[str], *arg_types: Box
    ) -> "Box":
        if not arg_types:
            return fn()
        arg_type, *new_arg_types = arg_types
        vname, *new_vnames = vnames
        return Abstraction.create(
            lambda x: cls.create_nary(Partial(fn, (x,)), new_vnames, *new_arg_types),
            arg_type,
            vname,
        )

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
    def create_native(
        cls,
        fn: typing.Callable[[T_box], U_box],
        can_call: typing.Callable[[T_box], bool],
        rettype: U_box,
    ) -> "Abstraction[T_box, U_box]":
        """
        Used to create an abstraction that is only replaced
        when the fn that is called doesn't return NotImplemented.

        Only use when neccesary, it means that the body of the function won't appear
        in the graph, only as a python function.
        """
        return cls(NativeAbstractionData(fn, can_call), rettype)

    @classmethod
    def _create_nary_inner(cls, fn, rettype, new_can_calls, x):
        """
        Include this as seperate function, instead of using lambda, so we can compare
        equality in tests using partial on it.
        """
        return cls.create_nary_native(
            Partial(fn, (x,)), Abstraction(None, rettype), *new_can_calls
        )

    @classmethod
    def create_nary_native(
        cls,
        fn: typing.Callable[..., T_box],
        rettype: T_box,
        *can_calls: typing.Callable[[Box], bool]
    ) -> "Box":
        if not can_calls:
            return fn()
        can_call, *new_can_calls = can_calls

        new_rettype: Box = rettype
        for _ in range(len(new_can_calls)):
            new_rettype = Abstraction(None, new_rettype)

        return cls.create_native(
            Partial(
                cls._create_nary_inner,
                (fn, Abstraction(None, rettype), tuple(new_can_calls)),
            ),
            can_call,
            new_rettype,
        )

    @classmethod
    def const(cls, value: T_box) -> "Abstraction[Box, T_box]":
        return cls(ConstAbstractionData(value), rettype=value)

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
    if not isinstance(self.value, AbstractionData):
        return NotImplemented
    variable, body = self.value.variable, self.value.body
    if variable.value is body.value:
        return arg  # type: ignore

    return body._replace(
        map_children(
            body.value,
            lambda child: Abstraction(  # type: ignore
                AbstractionData(variable, child), child._replace(None)
            )(arg),
        )
    )


@register(ctx, Abstraction.__call__)
def __call___const(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    if not isinstance(self.value, ConstAbstractionData):
        return NotImplemented
    return self.value.value


@register(ctx, Abstraction.__call__)
def __call___native(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    #  type ignore b/c https://github.com/python/mypy/issues/5485
    if not isinstance(
        self.value, NativeAbstractionData
    ) or not self.value.can_call(  # type: ignore
        arg
    ):
        return NotImplemented
    return self.value.fn(arg)  # type: ignore


@register(ctx, Abstraction.compose)
def compose(
    self: Abstraction[T_box_contra, T_box_cov],
    other: Abstraction[U_box_contra, T_box_contra],
) -> Abstraction[U_box_contra, T_box_cov]:
    if not isinstance(self.value, AbstractionData) or not isinstance(
        other.value, AbstractionData
    ):
        return NotImplemented

    return Abstraction(
        AbstractionData(other.value.variable, self(other.value.body)), self.rettype
    )


@register(ctx, AbstractionData)
def η_reduction(variable: Box[Variable], body: T_box) -> Abstraction:
    """
    https://en.wikipedia.org/wiki/Lambda_calculus#%CE%B7-conversion

    λx.(f x) -> f

    If we have a structure that looks like:
        lambda a: AbstractionData(variable, body)(a)
    We should replace it with:
        AbstractionData(a, body)

    Otherwise if we have some other kind of abstraction, we can replace it without changing the arg.

    Needed to support chaning abstraction wrapping list into list
    so we can compile list: lambda a: (1, 2, 3)(a) -> (1, 2, 3)
    """
    if not isinstance(body.value, Operation) or body.value.name != Abstraction.__call__:
        return NotImplemented
    inner_abstraction, inner_arg = body.value.args
    if inner_arg.value != variable.value:
        return NotImplemented

    if isinstance(inner_abstraction.value, AbstractionData):
        return inner_abstraction._replace(
            AbstractionData(
                inner_abstraction.value.variable._replace(variable.value),
                inner_abstraction.value.body,
            )
        )
    elif concrete(inner_abstraction.value):
        return inner_abstraction
    return NotImplemented


created_variables: typing.List[Variable] = []


def infinite_variables() -> typing.Iterator[Variable]:
    i = 0
    while True:
        # create a new variable if we haven't gotten this far yet.
        if i == len(created_variables):
            created_variables.append(Variable())
        yield created_variables[i]
        i += 1


def rename_variables(expr: T_box) -> T_box:
    """
    Renames variables according to alpha renaming, so that two
    expressions that have been alpha renamed will have some variables

    https://en.wikipedia.org/wiki/Lambda_calculus#α-conversion
    """
    replaced: typing.Dict[Variable, Variable] = {}
    variables = infinite_variables()
    # Iterate through graph.
    # every time we see a variable, we check if we have already replaced it.
    # if so, use that value.

    # otherwise, get a new fresh variable replace it and record it
    def inner(e: U_box) -> U_box:
        value = e.value
        new_value: typing.Any
        if isinstance(value, Variable):
            if value not in replaced:
                replaced[value] = next(variables)
            new_value = replaced[value]
        else:
            new_value = map_children(value, inner)
        return e._replace(new_value)

    return inner(expr)
