import typing
import dataclasses

from ..dispatch import *
from .abstractions import *
from .booleans import *
from .context import *
from .naturals import *

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
    value: typing.Any
    dtype: T_box

    @property
    def abstraction(self):
        return Abstraction(self.value, self.dtype)

    @classmethod
    def from_abstraction(cls, a: Abstraction[Nat, T_box]) -> "List[T_box]":
        return cls(a.value, a.rettype)

    @classmethod
    def create(cls, dtype: T_box, *args: T_box) -> "List[T_box]":
        return cls(tuple(args), dtype)

    @classmethod
    def create_infer(cls, arg: T_box, *args: T_box) -> "List[T_box]":
        return cls.create(arg.replace(None), arg, *args)

    @classmethod
    def from_function(cls, fn: typing.Callable[[Nat], T_box]) -> "List[T_box]":
        return cls.from_abstraction(Abstraction.create(fn, Nat(None)))

    def __getitem__(self, index: Nat) -> T_box:
        op = Operation(List.__getitem__, (self, index))
        return self.dtype.replace(op)

    # TODO: Refactor many of these to __getitem__ slices

    def first(self) -> T_box:
        """
        x[0]
        """
        return self.dtype.replace(Operation(List.first, (self,)))

    def rest(self) -> "List[T_box]":
        """
        x[1:]
        """
        return self.replace(Operation(List.rest, (self,)))

    def push(self, item: T_box) -> "List[T_box]":
        return self.replace(Operation(List.push, (self, item)))

    def append(self, length: Nat, item: T_box) -> "List[T_box]":
        return self.replace(Operation(List.append, (self, length, item)))

    def concat(self, length: Nat, other: "List[T_box]") -> "List[T_box]":
        return self.replace(Operation(List.concat, (self, length, other)))

    def drop(self, n: Nat) -> "List[T_box]":
        """
        Drops the first n items from the list.

        x[n:]
        """
        return self.replace(Operation(List.drop, (self, n)))

    def take(self, n: Nat) -> "List[T_box]":
        """
        x[:n]
        """
        return self.replace(Operation(List.take, (self, n)))

    def reverse(self, length: Nat) -> "List[T_box]":
        """
        x[::-1]
        """
        return self.replace(Operation(List.reverse, (self, length)))

    def reduce(
        self,
        length: Nat,
        initial: V_box,
        op: Abstraction[V_box, Abstraction[T_box, V_box]],
    ) -> V_box:
        return initial.replace(Operation(List.reduce, (self, length, initial, op)))

    def reduce_fn(
        self, length: Nat, initial: V_box, op: typing.Callable[[V_box, V_box], V_box]
    ) -> V_box:
        abs_: Abstraction[V_box, Abstraction[V_box, V_box]] = Abstraction.create_bin(
            op, initial.replace(None), initial.replace(None)
        )
        return self.reduce(length, initial, abs_)


@register(ctx, List.__getitem__)
def __getitem__(self: List[T_box], index: Nat) -> T_box:
    """
    Getitem translates into an abstraction.
    """
    return self.abstraction(index)


@register(ctx, Abstraction.__call__)
def __call___list(self: Abstraction[T_box, U_box], arg: T_box) -> U_box:
    if isinstance(self.value, tuple) and isinstance(arg.value, int):
        # We normally shouldn't get invalid indices
        # but sometimes we do, for example if we have a conditional  and two paths,
        # one might lead to invalid indices, but that's OK if it is never reached, i.e.
        # if conditional is always true.
        #
        # Alternative way would be to not evaluate conditional paths until we know which branch to take
        # but this hides part of the try and means we can't compile unknown conditionals
        try:
            return self.value[arg.value]
        except IndexError:
            # TODO: Return bottom type here, to show that this path is impossible.
            return NotImplemented
    return NotImplemented


@register(ctx, List.rest)
def rest(self: List[T_box]) -> List[T_box]:
    if isinstance(self.value, tuple):
        return self.replace(self.value[1:])
    # If we know the result is not going to be a tuple, implement with abstractions
    if concrete(self.value):
        return List.from_function(lambda i: self[i + Nat(1)])
    return NotImplemented


@register(ctx, List.push)
def push(self: List[T_box], item: T_box) -> List[T_box]:
    if isinstance(self.value, tuple):
        return self.replace((item,) + self.value)
    if concrete(self.value):
        return List.from_function(lambda i: i.equal(Nat(0)).if_(item, self[i - Nat(1)]))
    return NotImplemented


@register(ctx, List.append)
def append(self: List[T_box], length: Nat, item: T_box) -> List[T_box]:
    if isinstance(self.value, tuple):
        return self.replace(self.value + (item,))
    if concrete(self.value):
        return List.from_function(lambda i: i.equal(length).if_(item, self[i]))
    return NotImplemented


@register(ctx, List.concat)
def concat(self: List[T_box], length: Nat, other: List[T_box]) -> List[T_box]:
    if isinstance(self.value, tuple) and isinstance(other.value, tuple):
        return self.replace(self.value + other.value)
    if concrete(self.value) and concrete(other.value):
        return List.from_function(
            lambda i: i.lt(length).if_(self[i], other[i - length])
        )
    return NotImplemented


@register(ctx, List.concat)
def concat_empty_left(
    self: List[T_box], length: Nat, other: List[T_box]
) -> List[T_box]:
    if not isinstance(self.value, tuple) or self.value:
        return NotImplemented
    return other


@register(ctx, List.concat)
def concat_empty_right(
    self: List[T_box], length: Nat, other: List[T_box]
) -> List[T_box]:
    if not isinstance(other.value, tuple) or other.value:
        return NotImplemented
    return self


# @register(ctx, List.concat)
# def concat_abs(self: List[T_box], length: Nat, other: List[T_box]) -> List[T_box]:
#     if not concrete(self.value) or not concrete(other.value):
#         return NotImplemented

#     def new_list(idx: Nat) -> T_box:
#         return idx.lt(length).if_(
#             self.abstraction(idx), other.abstraction(idx - length)
#         )

#     return List.from_abstraction(Abstraction.create(new_list, Nat(None)))


@register(ctx, List.drop)
def drop(self: List[T_box], n: Nat) -> List[T_box]:
    if isinstance(self.value, tuple) and isinstance(n.value, int):
        return self.replace(self.value[n.value:])
    # TODO: make this a bit more permissive. If either self or n are concrete and not the right types
    # we can use general definition.
    if concrete(self) and concrete(n):
        return List.from_function(lambda i: self[i + n])
    return NotImplemented


@register(ctx, List.drop)
def drop_zero(self: List[T_box], n: Nat) -> List[T_box]:
    if n.value != 0:
        return NotImplemented
    return self


@register(ctx, List.take)
def take(self: List[T_box], n: Nat) -> List[T_box]:
    if isinstance(self.value, tuple) and isinstance(n.value, int):
        return self.replace(self.value[: n.value])
    if concrete(self) and concrete(n):
        return self
    return NotImplemented


@register(ctx, List.reverse)
def reverse(self: List[T_box], length: Nat) -> List[T_box]:
    if isinstance(self.value, tuple):
        return self.replace(self.value[::-1])
    if concrete(self):
        return self.from_function(lambda i: self[(length - Nat(1)) - i])
    return NotImplemented


@register(ctx, List.first)
def first(self: List[T_box]) -> T_box:
    return self[Nat(0)]


@register(ctx, List.reduce)
def reduce(
    self: List[T_box],
    length: Nat,
    initial: V_box,
    op: Abstraction[V_box, Abstraction[T_box, V_box]],
) -> V_box:
    def fn(v: V_box, idx: Nat) -> V_box:
        return op(v)(self[idx])

    abstraction = Abstraction.create_bin(fn, initial.replace(None), Nat(None))
    return length.loop(initial, abstraction)


@register(ctx, List.take)
def take_of_concat(self: List[T_box], n: Nat) -> List[T_box]:
    """
    When taking less than concat, just take left side
    """

    if (
        not isinstance(n.value, int)
        or not isinstance(self.value, Operation)
        or self.value.name != List.concat
        or not isinstance(self.value.args[1].value, int)
        or n.value > self.value.args[1].value
    ):
        return NotImplemented
    return self.value.args[0]


@register(ctx, List.drop)
def drop_of_concat(self: List[T_box], n: Nat) -> List[T_box]:
    """
    When dropping first part of concat, just take right side
    """

    if (
        not isinstance(n.value, int)
        or not isinstance(self.value, Operation)
        or self.value.name != List.concat
        or not isinstance(self.value.args[1].value, int)
        or n.value != self.value.args[1].value
    ):
        return NotImplemented
    return self.value.args[2]
