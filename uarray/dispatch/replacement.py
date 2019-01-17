import typing

from .spec import *

from .core import *

__all__ = ["register"]

T_call = typing.TypeVar("T_call", bound=typing.Callable)


def register(
    context: MutableContextType, target: T_call
) -> typing.Callable[[T_call], None]:
    def inner(fn: T_call, context=context) -> None:
        def replacement(op: object) -> object:
            args = children(op)
            try:
                resulting_wrapping = fn(*args)
            except Exception:
                raise Exception(f"Trying to replace {op} by calling {fn} with {args}")
            if resulting_wrapping == NotImplemented:
                return NotImplemented
            return resulting_wrapping.value.value

        context[target] = replacement

    return inner


# T_replacement = typing.TypeVar("T_replacement", bound=ReplacementType)

# def register(
#     ctx: MutableContextType, target: T_call
# ) -> typing.Callable[[T_call], None]:
#     def inner(fn: T_replacement, ctx=ctx) -> T_replacement:
#         ctx[fn.__name__] = fn
#         return fn

#     return inner


# @functools.singledispatch
# def replacement_key(replacement: ReplacementType) -> KeyType:
#     return replacement.__name__


# def register(
#     ctx: MutableContextType
# ) -> typing.Callable[[T_replacement], T_replacement]:
#     def inner(fn: T_replacement, ctx=ctx) -> T_replacement:
#         ctx[fn.__name__] = fn
#         return fn

#     return inner


# @replacement_key.register
# def _specreplacement_key(sr: SpecReplacement) ->


##
# Examples
##

# ctx: MutableContextType = {}


# def double(a: Box) -> Box:
#     return Box(Operation("add", [a, a]))


# @register(ctx)
# @SpecReplacement.decorator
# def hi(a: int, b: int) -> int:
#     return a + b


# # turns into


# def replace_hi(b: Box[Operation]) -> Box:
#     args = b.inside.args
#     if (
#         len(args) != 2
#         or not isinstance(args[0].inside, int)
#         or not isinstance(args[1].inside, int)
#     ):
#         return NotImplemented
#     return Box(args[0].inside + args[1].inside)


# T_nat = typing.TypeVar("T_nat", bound="Nat")


# class Nat(typing_extensions.Protocol):
#     @classmethod
#     def create(cls, value: int) -> "Nat":
#         ...

#     @abc.abstractmethod
#     def __add__(self: T_nat, other: T_nat) -> T_nat:
#         ...


# # # Turns into (when injected):


# # class NatInjected(Nat):
# #     def __init__(self, box: Box):
# #         self.box = Box

# #     @classmethod
# #     def create(cls, value: int) -> "NatInjected":
# #         return NatInjected(Box(Operation(Nat.create, [Box(value)])))

# #     def __add__(self, other: "NatInjected") -> "NatInjected":
# #         return NatInjected(Box(Operation(Nat.__add__, [self.box, other.box])))


# def double_again(a: T_nat) -> T_nat:
#     return a + a


# # turns into


# def double_again_transforme(b: Box) -> Box:
#     return double_again(NatInjected(b)).box


# class NatImpl(Nat):
#     def __init__(self, value: int):
#         self.value = value

#     @classmethod
#     def create(cls, value: int) -> "NatImpl":
#         return cls(value)

#     def __add__(self: "NatImpl", other: "NatImpl") -> "NatImpl":
#         return NatImpl(self.value + other.value)


# # registers methods


# def register_create(box: Box) -> Box:
#     args = box.inside.args
#     if len(args) != 1 or not isinstance(args[0].inside, int):
#         return NotImplemented
#     return args[0]


# ctx[Nat.create] = register_create


# def register_add(box: Box) -> Box:
#     args = box.inside.args
#     if len(args) != 1 or not isinstance(args[0].inside, int):
#         return NotImplemented
#     return args[0]


# ctx[Nat.__add__] = register_add
