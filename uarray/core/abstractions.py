"""
Lambda calculus
"""
import dataclasses
import typing
import copy

from ..dispatch import *
from .context import *

__all__ = ["Abstraction"]

T_wrapper = typing.TypeVar("T_wrapper", bound=Wrapper)
U_wrapper = typing.TypeVar("U_wrapper", bound=Wrapper)
VariableType = Box[typing.Any]


@dataclasses.dataclass
class AbstractionOperation(typing.Generic[T_wrapper]):
    variable: VariableType
    body: Box[T_wrapper]


@children.register(AbstractionOperation)
def abstraction_op_children(
    aop: AbstractionOperation[T_wrapper]
) -> typing.Tuple[VariableType, Box[T_wrapper]]:
    return (aop.variable, aop.body)


class Abstraction(
    Wrapper[AbstractionOperation[U_wrapper]], typing.Generic[T_wrapper, U_wrapper]
):
    """
    Abstraction from type T_wrapper to type U_wrapper.
    """

    def __call__(self, arg: T_wrapper) -> U_wrapper:
        return type(self.value.value.body.value)(
            Box(Operation(Abstraction.__call__, [self, arg]))
        )

    @classmethod
    def create(
        cls,
        fn: typing.Callable[[T_wrapper], U_wrapper],
        wrap_var: typing.Callable[[VariableType], T_wrapper],
    ) -> "Abstraction[T_wrapper, U_wrapper]":
        variable = Box(None)
        return cls(Box(AbstractionOperation(variable, Box(fn(wrap_var(variable))))))

    @classmethod
    def const(cls, value: T_wrapper) -> "Abstraction[Wrapper[typing.Any], T_wrapper]":
        return cls.create(lambda _: value, lambda var: type(value)(var))

    @classmethod
    def identity(
        cls, wrapper_type: typing.Type[T_wrapper]
    ) -> "Abstraction[T_wrapper, T_wrapper]":
        return cls.create(lambda v: v, lambda var: wrapper_type(var))


@register(ctx, Abstraction.__call__)
def apply_abstraction(
    self: Abstraction[T_wrapper, U_wrapper], arg: T_wrapper
) -> U_wrapper:
    # copy so that we can replace without replacing original abstraction
    abstraction_op = copy.deepcopy(self.value.value)
    abstraction_op.variable.value = arg
    return abstraction_op.body.value


# def variable():
#     return Operation("variable", ())


# @dataclasses.dataclass
# class Bottom:
#     """
#     Value that should never be returned by a function.
#     (for example the getitem function for an empty list should return this type)

#     https://en.wikipedia.org/wiki/Bottom_type
#     """

#     pass


# bottom = Bottom()


# @dataclasses.dataclass
# class Variable:
#     name: typing.Optional[str] = None


# # @dataclasses.dataclass
# # class Abstraction(typing.Generic[T]):
# #     variable: Box[Variable]
# #     body: Box[T]


# # @children.register
# # def _abstraction_children(a: Abstraction):
# #     return (a.variable, a.body)


# # @dataclasses.dataclass
# # class Apply(typing.Generic[T, V]):
# #     abstraction: Box[Abstraction[T]]
# #     arg: Box[V]


# # @children.register
# # def _apply_children(a: Apply):
# #     return (a.abstraction, a.arg)


# # def replace_apply(b: Box[Apply[T, V]]) -> Box[T]:
# #     apply = b.inside

# #     abstraction = apply.abstraction.inside
# #     arg = apply.arg.inside

# #     # rewrite inside of variable to be arg
# #     variable_box: Box = abstraction.variable
# #     variable_box.inside = arg

# #     # return body, arg has now been replaced
# #     return abstraction.body


# # class Abstrea


# class AbstractionProtocol(typing_extensions.Protocol[T, V]):
#     @classmethod
#     @abc.abstractmethod
#     def create(cls, fn: typing.Callable[[T], V]) -> AbstractionProtocol[T, V]:
#         ...

#     @classmethod
#     def create_bin(
#         cls, fn: typing.Callable[[T, U], V]
#     ) -> AbstractionProtocol[T, AbstractionProtocol[U, V]]:
#         return cls.create(lambda t: cls.create(lambda u: fn(t, u)))

#     def __call__(self, arg: T) -> V:
#         ...


# @dataclasses.dataclass
# class Abstraction(AbstractionProtocol[T, V]):
#     abstraction: Abstraction

#     @classmethod
#     def create(cls, fn: typing.Callable[[T], V]) -> Abstraction[T, V]:
#         ...
#         # variable = Box(Variable())
#         # abstraction = Abstraction(variable, Box(fn(variable)))
#         # return AbstractionWrapper(abstraction)

#     @classmethod
#     def const(cls, val: V) -> Abstraction[typing.Any, V]:
#         return cls.create(lambda _: val)

#     @classmethod
#     def bottom(cls) -> Abstraction[typing.Any, typing.Any]:
#         return cls.create(lambda _: bottom)

#     def __call__(self, arg: T) -> V:
#         ...


# ?        return Box(Apply(self.abstraction, arg))
