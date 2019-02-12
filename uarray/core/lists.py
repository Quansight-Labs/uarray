import dataclasses
import typing

from .abstractions import *
from .context import *
from .naturals import *
from ..dispatch import *

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


__all__ = ["List"]


@children.register
def tuple_children(a: tuple):
    return a


@map_children.register
def tuple_map_children(a: tuple, b: typing.Callable):
    return tuple(map(b, a))


@dataclasses.dataclass
class List(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any = None
    dtype: T_box = typing.cast(T_box, Box())

    @property
    def abstraction(self):
        return Abstraction(self.value, self.dtype)

    @classmethod
    def from_abstraction(cls, a: Abstraction[Natural, T_box]) -> "List[T_box]":
        return cls(a.value, a.rettype)

    @classmethod
    def create_abstraction(cls, fn: typing.Callable[[Natural], T_box]) -> "List[T_box]":
        return cls.from_abstraction(Abstraction.create(fn, Natural()))

    def as_abstraction(self) -> "List[T_box]":
        return List.create_abstraction(lambda i: self[i])

    @classmethod
    def create(cls, dtype: T_box, *args: T_box) -> "List[T_box]":
        return cls(tuple(args), dtype)

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "List[T_box]":
        return cls.create(arg.replace(None), arg, *args)

    @classmethod
    def from_function(cls, fn: typing.Callable[[Natural], T_box]) -> "List[T_box]":
        return cls.from_abstraction(Abstraction.create(fn, Natural()))

    def __getitem__(self, index: Natural) -> T_box:
        return self.abstraction(index)

    @operation_with_default(ctx)
    def first(self) -> T_box:
        """
        x[0]
        """
        return self[Natural(0)]

    @operation_with_default(ctx)
    def rest(self) -> "List[T_box]":
        """
        x[1:]
        """
        return List.from_function(lambda i: self[i + Natural(1)])

    @operation_with_default(ctx)
    def push(self, item: T_box) -> "List[T_box]":
        return List.from_function(
            lambda i: i.equal(Natural(0)).if_(item, self[i - Natural(1)])
        )

    @operation_with_default(ctx)
    def append(self, length: Natural, item: T_box) -> "List[T_box]":
        return List.from_function(lambda i: i.equal(length).if_(item, self[i]))

    @operation_with_default(ctx)
    def concat(self, length: Natural, other: "List[T_box]") -> "List[T_box]":
        return List.from_function(
            lambda i: i.lt(length).if_(self[i], other[i - length])
        )

    @operation_with_default(ctx)
    def drop(self, n: Natural) -> "List[T_box]":
        """
        Drops the first n items from the list.

        x[n:]
        """
        return List.from_function(lambda i: self[i + n])

    @operation_with_default(ctx)
    def take(self, n: Natural) -> "List[T_box]":
        """
        x[:n]
        """
        return self

    @operation_with_default(ctx)
    def reverse(self, length: Natural) -> "List[T_box]":
        """
        x[::-1]
        """
        return self.from_function(lambda i: self[(length - Natural(1)) - i])

    @operation_with_default(ctx)
    def reduce(
        self,
        length: Natural,
        initial: V_box,
        op: Abstraction[V_box, Abstraction[T_box, V_box]],
    ) -> V_box:
        def fn(v: V_box, idx: Natural) -> V_box:
            return op(v)(self[idx])

        abstraction = Abstraction.create_bin(fn, initial.replace(None), Natural())
        return length.loop(initial, abstraction)

    def reduce_fn(
        self,
        length: Natural,
        initial: V_box,
        op: typing.Callable[[V_box, T_box], V_box],
    ) -> V_box:
        abs_ = Abstraction.create_bin(op, initial.replace(None), self.dtype)
        return self.reduce(length, initial, abs_)


@register(ctx, Abstraction.__call__)
def __call___list(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    tpl = extract_value(tuple, self)
    idx = extract_value(int, arg)
    # We normally shouldn't get invalid indices
    # but sometimes we do, for example if we have a conditional  and two paths,
    # one might lead to invalid indices, but that's OK if it is never reached, i.e.
    # if conditional is always true.
    try:
        return tpl[idx]
    except IndexError:
        # TODO: Return bottom type here, to show that this path is impossible.
        return NotImplemented


@register(ctx, List.rest)
def rest_tuple(self: List[T_box]) -> List[T_box]:
    return self.replace(extract_value(tuple, self)[1:])


@register(ctx, List.push)
def push_tuple(self: List[T_box], item: T_box) -> List[T_box]:
    return self.replace((item,) + extract_value(tuple, self))


@register(ctx, List.append)
def append_tuple(self: List[T_box], length: Natural, item: T_box) -> List[T_box]:
    return self.replace(extract_value(tuple, self) + (item,))


@register(ctx, List.concat)
def concat_tuple(self: List[T_box], length: Natural, other: List[T_box]) -> List[T_box]:
    return self.replace(extract_value(tuple, self) + extract_value(tuple, other))


@register(ctx, List.concat)
def concat_empty_left(
    self: List[T_box], length: Natural, other: List[T_box]
) -> List[T_box]:
    if not extract_value(tuple, self):
        return other
    return NotImplemented


@register(ctx, List.concat)
def concat_empty_right(
    self: List[T_box], length: Natural, other: List[T_box]
) -> List[T_box]:
    if not extract_value(tuple, other):
        return self
    return NotImplemented


@register(ctx, List.drop)
def drop_tuple(self: List[T_box], n: Natural) -> List[T_box]:
    return self.replace(extract_value(tuple, self)[extract_value(int, n) :])


@register(ctx, List.drop)
def drop_zero(self: List[T_box], n: Natural) -> List[T_box]:
    if extract_value(int, n) == 0:
        return self
    return NotImplemented


@register(ctx, List.take)
def take_tuple(self: List[T_box], n: Natural) -> List[T_box]:
    return self.replace(extract_value(tuple, self)[: extract_value(int, n)])


@register(ctx, List.reverse)
def reverse_tuple(self: List[T_box], length: Natural) -> List[T_box]:
    return self.replace(extract_value(tuple, self)[::-1])


@register(ctx, List.first)
def first_tuple(self: List[T_box]) -> T_box:
    return extract_value(tuple, self)[0]


# TODO: implement reduce special case on tuple


@register(ctx, List.take)
def take_of_concat(self: List[T_box], n: Natural) -> List[T_box]:
    """
    When taking less than concat, just take left side
    """
    l, length, r = extract_args(List.concat, self)  # type: ignore
    if extract_value(int, n) <= extract_value(int, length):
        return l
    return NotImplemented


@register(ctx, List.drop)
def drop_of_concat(self: List[T_box], n: Natural) -> List[T_box]:
    """
    When dropping first part of concat, just take right side
    """

    l, length, r = extract_args(List.concat, self)  # type: ignore
    if extract_value(int, n) == extract_value(int, length):
        return r
    return NotImplemented
