import typing
import dataclasses
import functools

from .core import *

__all__ = ["Operation", "operation", "concrete_operation"]
T_box = typing.TypeVar("T_box", bound="Box")
T_args = typing.TypeVar("T_args", bound=ChildrenType)
T_call = typing.TypeVar("T_call", bound=typing.Callable)


@dataclasses.dataclass(frozen=True)
class Operation(typing.Generic[T_box, T_args]):
    name: typing.Callable[..., T_box]
    args: T_args
    concrete: bool = False


def operation(type_mapping: T_call) -> T_call:
    """
    Registers a function as an operation.
    """

    @functools.wraps(type_mapping)
    def inner(*args):
        restype = type_mapping(*args)
        return restype.replace(Operation(inner, tuple(args)))

    return typing.cast(T_call, inner)


def concrete_operation(type_mapping: T_call) -> T_call:
    """
    Registers a function as an operation.
    """

    @functools.wraps(type_mapping)
    def inner(*args):
        restype = type_mapping(*args)
        return restype.replace(Operation(inner, tuple(args), True))

    return typing.cast(T_call, inner)


@concrete.register
def operation_concrete(x: Operation) -> bool:
    return x.concrete


@children.register(Operation)
def operation_children(op: Operation[T_box, T_args]) -> T_args:
    return op.args


@key.register
def operation_key(op: Operation) -> object:
    return op.name


@map_children.register
def operation_map_children(
    v: Operation, fn: typing.Callable[[typing.Any], typing.Any]
) -> Operation:
    return dataclasses.replace(v, args=tuple(map(fn, v.args)))
