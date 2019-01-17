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
        cls, fn: typing.Callable[[T_box], U_box], arg_type: typing.Type[T_box]
    ) -> "Abstraction[T_box, U_box]":
        variable: T_box = arg_type(None)
        return cls(Operation(Abstraction, (variable, fn(variable))))

    @classmethod
    def create_bin(
        cls,
        fn: typing.Callable[[T_box, U_box], V_box],
        arg1_type: typing.Type[T_box],
        arg2_type: typing.Type[U_box],
    ) -> "Abstraction[T_box, Abstraction[U_box, V_box]]":
        return cls.create(
            lambda arg1: cls.create(lambda arg2: fn(arg1, arg2), arg2_type), arg1_type
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
    variable.value = arg.value
    return body


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
