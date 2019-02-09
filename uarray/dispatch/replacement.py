import typing

from .core import MutableContextType, children, Box

__all__ = ["register", "register_type"]
T = typing.TypeVar("T")
V = typing.TypeVar("V")
T_call = typing.TypeVar("T_call", bound=typing.Callable)


@typing.overload
def register(
    context: MutableContextType, target: typing.Type
) -> typing.Callable[[T_call], T_call]:
    ...


@typing.overload
def register(
    context: MutableContextType, target: T_call
) -> typing.Callable[[T_call], T_call]:
    ...


@typing.overload
def register(
    context: MutableContextType, target: str
) -> typing.Callable[[T_call], T_call]:
    ...


def register(
    context: MutableContextType, target: typing.Union[T_call, typing.Type, str]
) -> typing.Callable[[T_call], T_call]:
    def inner(fn: T_call, context=context) -> T_call:
        def replacement(op: Box) -> Box:
            args = children(op.value)
            try:
                resulting_box = fn(*args)
            except Exception:
                raise Exception(
                    f"Trying to replace {type(op)} by calling {fn} with {tuple(map(type, args))}: {repr(op)}"
                )
            return resulting_box

        context[target] = replacement
        return fn

    return inner


def register_type(
    context: MutableContextType, target: typing.Type[T]
) -> typing.Callable[[typing.Callable[[T], V]], typing.Callable[[T], V]]:
    def inner(fn: typing.Callable[[T], V], context=context) -> typing.Callable[[T], V]:
        def replacement(b: Box[T]) -> Box[V]:
            v = b.value
            if not isinstance(v, target):
                return NotImplemented
            resulting_val = fn(v)
            return typing.cast(  # need cast b/c mypy cant have generic of bound var
                Box[V], b.replace(resulting_val)
            )

        context[target] = replacement
        return fn

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
