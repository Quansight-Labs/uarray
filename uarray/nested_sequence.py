"""
Support compiling to, and reading from, nested python tuples as arrays.
"""
import dataclasses
import itertools
import typing

from .core import *
from .dispatch import *

T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")
ctx = MapChainCallable()
default_context.append(ctx)

__all__ = ["create_python_array", "to_python_array", "create_python_bin_abs"]


@dataclasses.dataclass(frozen=True)
class NestedTuples:
    value: typing.Any


def create_python_array(shape: typing.Tuple[int, ...], data: typing.Any) -> Array:
    return Array.create(
        Array.create_shape(*map(Natural, shape)), Abstraction(NestedTuples(data), Box())
    )


def index_python_array(array: Array[T_box], *idx: Natural) -> T_box:
    ...


@register(ctx, Abstraction.__call__)
def __call___nested_lists(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    if (
        not (isinstance(self.value, NestedTuples))
        or not isinstance(arg.value, Operation)
        or arg.value.name != Vec.create
    ):
        return NotImplemented
    idx = arg.value.args[1].value
    if not isinstance(idx, tuple):
        return NotImplemented

    data = self.value.value
    for i in idx:
        if not isinstance(i.value, int):
            return NotImplemented
        data = data[i.value]
    return self.rettype.replace(data)


@operation
def to_python_array(a: Array[T_box]) -> Array[T_box]:
    return a


@register(ctx, to_python_array)
def _to_python_array(a: Array[T_box]) -> Array[T_box]:
    return to_python_array_expanded_first(a.shape, a.idx_abs)


@operation
def to_python_array_expanded_first(
    shape: Vec[Natural], idx_abs: Abstraction[Vec[Natural], T_box]
) -> Array[T_box]:
    return Array(dtype=idx_abs.rettype)


@register(ctx, to_python_array_expanded_first)
def _to_python_array_expanded_first(
    shape: Vec[Natural], idx_abs: Abstraction[Vec[Natural], T_box]
) -> Array[T_box]:
    # If contents are already nested tuples, we can stop now.
    if isinstance(idx_abs.value, NestedTuples):
        return Array.create(shape, idx_abs)
    if not isinstance(shape.value, Operation) or shape.value.name != Vec.create:
        return NotImplemented
    shape_list = shape.value.args[1]
    if not isinstance(shape_list.value, tuple):
        return NotImplemented
    shape_items: typing.Tuple[Natural, ...] = shape_list.value
    if not all(isinstance(i, int) for i in shape_items):
        return NotImplemented
    shape_items_ints: typing.Tuple[int, ...] = tuple(i.value for i in shape_items)

    # iterate through all combinations of shape list
    # create list that has all of these
    all_possible_idxs = list(itertools.product(*(range(i) for i in shape_items_ints)))

    contents = List.create(
        idx_abs.rettype,
        *(idx_abs(Array.create_shape(*map(Natural, idx))) for idx in all_possible_idxs)
    )

    return to_python_array_expanded(shape, contents)


@operation
def to_python_array_expanded(
    shape: Vec[Natural], contents: List[T_box]
) -> Array[T_box]:
    return Array(dtype=contents.dtype)


@register(ctx, to_python_array_expanded)
def _to_python_array_expanded(
    shape: Vec[Natural], contents: List[T_box]
) -> Array[T_box]:
    if not isinstance(shape.value, Operation) or shape.value.name != Vec.create:
        return NotImplemented
    shape_length, shape_list = shape.value.args
    if not isinstance(shape_length.value, int) or not isinstance(
        shape_list.value, tuple
    ):
        return NotImplemented
    shape_items: typing.Tuple[Natural, ...] = shape_list.value
    if not all(isinstance(i.value, int) for i in shape_items):
        return NotImplemented

    if not isinstance(contents.value, tuple):
        return NotImplemented
    shape_items_ints: typing.Tuple[int, ...] = tuple(i.value for i in shape_items)

    all_possible_idxs = list(itertools.product(*(range(i) for i in shape_items_ints)))

    def inner(s, i):
        if s:
            return tuple(inner(s[1:], i + (idx,)) for idx in range(s[0]))

        flattened_idx = all_possible_idxs.index(i)
        content = contents.value[flattened_idx]
        if not isinstance(content, PythonScalar):
            return NotImplemented
        return content.value

    return create_python_array(shape_items_ints, inner(shape_items_ints, ()))


def create_python_bin_abs(
    fn: typing.Callable[[T, U], V], l_type: typing.Type[T], r_type: typing.Type[U]
) -> Abstraction[Box[T], Abstraction[Box[U], Box[V]]]:

    return Abstraction.create_nary_native(  # type: ignore
        lambda a, b: Box(fn(a.value, b.value)),
        Box(typing.cast(V, None)),
        lambda a: isinstance(a.value, l_type),
        lambda b: isinstance(b.value, r_type),
    )
