import typing
import itertools
from .core import *
from .dispatch import *

T_box = typing.TypeVar("T_box", bound=Box)
ctx = MapChainCallable()
default_context.append(ctx)

__all__ = ["create_python_array", "to_python_array"]


class PythonScalar(Box[typing.Any]):
    pass


# Add box around thes
def create_python_array(shape: typing.Tuple[int, ...], data: typing.Any) -> Array:
    return Array(Operation("python-array", (Box(shape), Box(data))), PythonScalar(None))


def is_python_array(a: Array) -> bool:
    return isinstance(a.value, Operation) and a.value.name == "python-array"


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not is_python_array(self):
        return NotImplemented
    return Array.create_shape(*map(Nat, self.value.args[0].value))


def index_python_array(array: Array[T_box], *idx: Nat) -> T_box:
    ...


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[List[Nat], T_box]:
    if not is_python_array(self):
        return NotImplemented

    dim = len(self.value.args[0].value)

    @Array.create_idx_abs
    def idx_abs(idx: List[Nat]) -> T_box:
        return self.dtype._replace(
            Operation(index_python_array, (self, *(idx[Nat(d)] for d in range(dim))))
        )

    return idx_abs


@register(ctx, index_python_array)
def _index_python_array(array: Array[T_box], *idx: Nat) -> T_box:
    if not is_python_array(array) or not all(i._concrete for i in idx):
        return NotImplemented

    data = array.value.args[1].value
    for i in idx:
        data = data[i.value]

    return array.dtype._replace(data)


def to_python_array(a: Array[T_box]) -> Array[T_box]:
    return Array(Operation(to_python_array, (a,)), a.dtype)


@register(ctx, to_python_array)
def _to_python_array(a: Array[T_box]) -> Array[T_box]:
    return to_python_array_expanded_first(a.shape, a.idx_abs)


def to_python_array_expanded_first(
    shape: Vec[Nat], idx_abs: Abstraction[List[Nat], T_box]
) -> Array[T_box]:
    return Array(
        Operation(to_python_array_expanded_first, (shape, idx_abs)), idx_abs.rettype
    )


@register(ctx, to_python_array_expanded_first)
def _to_python_array_expanded_first(
    shape: Vec[Nat], idx_abs: Abstraction[List[Nat], T_box]
) -> Array[T_box]:
    if not shape._concrete:
        return NotImplemented
    shape_length, shape_list = shape.value.args
    if not shape_list._concrete:
        return NotImplemented
    shape_items: typing.Tuple[Nat, ...] = shape_list.value.args
    if not all(i._concrete for i in shape_items):
        return NotImplemented
    shape_items_ints: typing.Tuple[int, ...] = tuple(i.value for i in shape_items)

    # iterate through all combinations of shape list
    # create list that has all of these
    all_possible_idxs = list(itertools.product(*(range(i) for i in shape_items_ints)))

    contents = List.create(
        idx_abs.rettype,
        *(idx_abs(List.create(Nat(None), *map(Nat, idx))) for idx in all_possible_idxs)
    )

    return to_python_array_expanded(shape, contents)


def to_python_array_expanded(shape: Vec[Nat], contents: List[T_box]) -> Array[T_box]:
    return Array(Operation(to_python_array_expanded, (shape, contents)), contents.dtype)


@register(ctx, to_python_array_expanded)
def _to_python_array_expanded(shape: Vec[Nat], contents: List[T_box]) -> Array[T_box]:
    if not shape._concrete:
        return NotImplemented
    shape_length, shape_list = shape.value.args
    if not shape_length._concrete or not shape_list._concrete:
        return NotImplemented
    shape_items: typing.Tuple[Nat, ...] = shape_list.value.args
    if not all(i._concrete for i in shape_items):
        return NotImplemented

    if not contents._concrete:
        return NotImplemented
    shape_items_ints: typing.Tuple[int, ...] = tuple(i.value for i in shape_items)

    all_possible_idxs = list(itertools.product(*(range(i) for i in shape_items_ints)))

    def inner(s, i):
        if s:
            return tuple(inner(s[1:], i + (idx,)) for idx in range(s[0]))

        flattened_idx = all_possible_idxs.index(i)
        content = contents.value.args[flattened_idx]
        if not isinstance(content, PythonScalar):
            return NotImplemented
        return content.value

    return create_python_array(shape_items_ints, inner(shape_items_ints, ()))
