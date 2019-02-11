import typing
import dataclasses
import functools

from .core import *
from .replacement import *

__all__ = [
    "Operation",
    "operation",
    "concrete_operation",
    "extract_args",
    "extract_value",
    "operation_with_default",
]
T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound="Box")
U_box = typing.TypeVar("U_box", bound="Box")
V_box = typing.TypeVar("V_box", bound="Box")
X_box = typing.TypeVar("X_box", bound="Box")
Y_box = typing.TypeVar("Y_box", bound="Box")
T_args = typing.TypeVar("T_args", bound=ChildrenType)
T_call = typing.TypeVar("T_call", bound=typing.Callable)


@dataclasses.dataclass(frozen=True)
class Operation(typing.Generic[T_box, T_args]):
    name: typing.Callable[..., T_box]
    args: T_args
    concrete: bool = False


@typing.overload
def extract_args(
    fn: typing.Callable[[U_box, V_box, X_box, Y_box], T_box], box: T_box
) -> typing.Tuple[U_box, V_box, X_box, Y_box]:
    ...


@typing.overload
def extract_args(
    fn: typing.Callable[[U_box, V_box, X_box], T_box], box: T_box
) -> typing.Tuple[U_box, V_box, X_box]:
    ...


@typing.overload
def extract_args(
    fn: typing.Callable[[U_box, V_box], T_box], box: T_box
) -> typing.Tuple[U_box, V_box]:
    ...


@typing.overload
def extract_args(
    fn: typing.Callable[[U_box], T_box], box: T_box
) -> typing.Tuple[U_box]:
    ...


@typing.overload
def extract_args(fn: typing.Callable[[], T_box], box: T_box) -> typing.Tuple:
    ...


def extract_args(fn: typing.Callable[..., T_box], box: T_box) -> typing.Tuple:
    if isinstance(box.value, Operation) and box.value.name == fn:
        return box.value.args
    raise ReturnNotImplemented


def extract_value(type: typing.Type[T], box: Box[typing.Any]) -> T:
    if isinstance(box.value, type):
        return box.value
    raise ReturnNotImplemented


def operation_with_default(
    context: MutableContextType
) -> typing.Callable[[T_call], T_call]:
    """
    Creates an operation and registers a default implementation.
    """

    def inner(default_impl: T_call, context=context) -> T_call:
        operation_fn = operation(default_impl)
        register(context, operation_fn, default=True)(default_impl)
        return operation_fn

    return inner


def operation(type_mapping: T_call) -> T_call:
    """
    Registers a function as an operation.
    """

    @functools.wraps(type_mapping)
    def inner(*args, type_mapping=type_mapping):
        restype = type_mapping(*args)
        return restype.replace(Operation(inner, tuple(args)))

    return typing.cast(T_call, inner)


def concrete_operation(type_mapping: T_call) -> T_call:
    """
    Registers a function as an operation.
    """

    @functools.wraps(type_mapping)
    def inner(*args, type_mapping=type_mapping):
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
