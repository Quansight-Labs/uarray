import typing
from udispatch import *
from uarray import *

T_box = typing.TypeVar("T_box", bound=Box)

__all__ = ["create_empty", "set_item", "create_and_fill"]


@operation
def create_empty(dtype: T_box, length: Natural) -> List[T_box]:
    return List(None, dtype)


@operation
def set_item(lst: List[T_box], index: Natural, item: T_box) -> List[T_box]:
    return lst.replace()


def create_and_fill(array: Array[T_box]) -> Array[T_box]:
    vec = array.ravel()
    n = vec.length
    return Array.from_list_nd(
        n.loop_abstraction(
            create_empty(vec.dtype, n), lambda res, i: set_item(res, i, vec[i])
        ),
        array.shape,
    )
