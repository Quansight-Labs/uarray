"""
Lambda calculus
"""
import dataclasses
import typing

from udispatch import *

__all__ = ["Abstraction", "Variable", "rename_variables", "Partial"]

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)
T_box_cov = typing.TypeVar("T_box_cov", bound=Box, covariant=True)
T_box_contra = typing.TypeVar("T_box_contra", bound=Box, contravariant=True)


@dataclasses.dataclass
class Partial(typing.Generic[T]):
    """
    Simple partial function application.

    We use this over functools.partial b/c it doesn't support
    equality (https://bugs.python.org/issue3564) and we need that for testing.
    """

    fn: typing.Callable[..., T]
    args: typing.Tuple

    def __call__(self, *args) -> T:
        return self.fn(*self.args, *args)  # type: ignore

    def __post_init__(self):
        if isinstance(self.fn, Partial):
            fn = self.fn
            self.fn = fn.fn
            self.args = fn.args + self.args


@dataclasses.dataclass(eq=False, frozen=True)
class Variable:
    name: typing.Optional[str] = None

    def __str__(self):
        return self.name or ""


@concrete.register
def variable_concrete(v: Variable):
    return False


@dataclasses.dataclass(frozen=True)
class NativeAbstraction(typing.Generic[T_box_cov]):
    fn: typing.Callable[[T_box], U_box]
    can_call: typing.Callable[[T_box], bool]


@dataclasses.dataclass
class Abstraction(Box[typing.Any], typing.Generic[T_box_contra, T_box_cov]):
    """
    Abstraction from type T_box_contra to type T_box_cov.
    """

    value: typing.Any = None
    # Need cast b/c
    # https://github.com/python/mypy/issues/3737
    rettype: T_box_cov = typing.cast(T_box_cov, Box())

    @operation
    def __call__(self, arg: T_box_contra) -> T_box_cov:
        return self.rettype

    @staticmethod
    @concrete_operation
    def from_variable(variable: T_box, body: U_box) -> "Abstraction[T_box, U_box]":
        return Abstraction(rettype=body.replace())

    @classmethod
    def create(
        cls, fn: typing.Callable[[T_box], U_box], arg_type: T_box, vname: str = None
    ) -> "Abstraction[T_box, U_box]":
        arg = arg_type.replace(Variable(vname))
        body = fn(arg)
        return cls.from_variable(arg, body)

    @classmethod
    def create_nary(
        cls, fn: typing.Callable[..., T_box], vnames: typing.List[str], *arg_types: Box
    ) -> "typing.Union[Abstraction, T_box]":  # cannot type this properly
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
        return cls(NativeAbstraction(fn, can_call), rettype)

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


@register(Abstraction.__call__)
def __call__(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    variable, body = extract_args(Abstraction.from_variable, self)
    if variable.value is body.value:
        return arg  # type: ignore

    return body.replace(
        map_children(
            body.value, lambda child: Abstraction.from_variable(variable, child)(arg)
        )
    )


@register(Abstraction.__call__)
def __call___native(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    native_abstraction = extract_value(NativeAbstraction, self)
    #  type ignore b/c https://github.com/python/mypy/issues/5485
    if not native_abstraction.can_call(arg):  # type: ignore
        return NotImplemented
    return native_abstraction.fn(arg)  # type: ignore


@register(Abstraction.from_variable)
def η_reduction(variable: T_box, body: U_box) -> Abstraction[T_box, U_box]:
    """
    https://en.wikipedia.org/wiki/Lambda_calculus#%CE%B7-conversion

    λx.(f x) -> f

    If we have a structure that looks like:
        lambda a: abstraction(variable, body)(a)
    We should replace it with:
        abstraction(a, body)

    Otherwise if we have some other kind of abstraction, we can replace it without changing the arg.

    Needed to support chaning abstraction wrapping list into list
    so we can compile list: lambda a: (1, 2, 3)(a) -> (1, 2, 3)
    """
    inner_abstraction, inner_arg = extract_args(  # type: ignore
        Abstraction.__call__, body
    )
    if inner_arg.value != variable.value:
        return NotImplemented

    try:
        inner_variable, inner_body = extract_args(
            Abstraction.from_variable, inner_abstraction
        )
    except ReturnNotImplemented:
        pass
    else:
        return Abstraction.from_variable(
            inner_variable.replace(variable.value), inner_body
        )
    if concrete(inner_abstraction.value):
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
        return e.replace(new_value)

    return inner(expr)
