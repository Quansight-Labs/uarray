import dataclasses
import operator
import typing

from .core import *
from .dispatch import *

__all__ = ["MoA"]


ctx = MapChainCallable()

default_context.append(ctx)

T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


@dataclasses.dataclass
class MoA(Box[typing.Any], typing.Generic[T_box]):
    value: typing.Any = None
    dtype: T_box = typing.cast(T_box, Box(None))

    @property
    def array(self):
        return Array(self.value, self.dtype)

    @classmethod
    def from_array(cls, a: Array[T_box]) -> "MoA[T_box]":
        return cls(a.value, a.dtype)

    @property
    def dim(self) -> "MoA[Natural]":
        return self._dim()

    @operation
    def _dim(self) -> "MoA[Natural]":
        return MoA(dtype=Natural())

    @property
    def shape(self) -> "MoA[Natural]":
        return self._shape()

    @operation
    def _shape(self) -> "MoA[Natural]":
        return MoA(dtype=Natural())

    @operation
    def __getitem__(self, idxs: "MoA[Natural]") -> "MoA[T_box]":
        return self

    @operation
    def unary_operation(self, op: Abstraction[T_box, U_box]) -> "MoA[U_box]":
        return MoA(dtype=op.rettype)

    def unary_operation_abstraction(
        self, op: typing.Callable[[T_box], U_box]
    ) -> "MoA[U_box]":
        return self.unary_operation(Abstraction.create(op, self.dtype))

    @operation
    def binary_operation(
        self, op: Abstraction[T_box, Abstraction[U_box, V_box]], other: "MoA[U_box]"
    ) -> "MoA[V_box]":
        return MoA(dtype=op.rettype.rettype)

    def binary_operation_abstraction(
        self, op: typing.Callable[[T_box, U_box], V_box], other: "MoA[U_box]"
    ) -> "MoA[V_box]":
        return self.binary_operation(
            Abstraction.create_bin(op, self.dtype, other.dtype), other
        )

    @operation
    def transpose(self) -> "MoA[T_box]":
        return self

    @operation
    def outer_product(
        self: "MoA[T_box]",
        op: Abstraction[T_box, Abstraction[U_box, V_box]],
        other: "MoA[U_box]",
    ) -> "MoA[V_box]":
        return MoA(dtype=op.rettype.rettype)

    def outer_product_abstraction(
        self: "MoA[T_box]",
        op: typing.Callable[[T_box, U_box], V_box],
        other: "MoA[U_box]",
    ) -> "MoA[V_box]":
        return self.outer_product(
            Abstraction.create_bin(op, self.dtype, other.dtype), other
        )

    def __add__(self, other: "MoA[T_box]") -> "MoA[T_box]":
        """
        Assumes T_box supports __add__
        """
        return self.binary_operation_abstraction(operator.add, other)

    @operation
    def reduce(
        self: "MoA[T_box]",
        op: Abstraction[V_box, Abstraction[T_box, V_box]],
        initial: V_box,
    ) -> "MoA[V_box]":
        return MoA(dtype=op.rettype.rettype)

    def reduce_abstraction(
        self: "MoA[T_box]", op: typing.Callable[[V_box, T_box], V_box], initial: V_box
    ) -> "MoA[V_box]":
        return self.reduce(Abstraction.create_bin(op, initial, self.dtype), initial)

    @staticmethod
    @operation
    def gamma(idx: Vec[Natural], shape: Vec[Natural]) -> Natural:
        return Natural()

    @classmethod
    def from_list_nd(cls, data: List[T_box], shape: Vec[Natural]) -> "MoA[T_box]":
        @Array.create_idx_abs
        def idx_abs(idx: Vec[Natural]) -> T_box:
            return data[gamma(idx, shape)]

        return MoA.from_array(Array.create(shape, idx_abs))


@register(ctx, MoA._dim)
def _dim(self: MoA[T_box]) -> "MoA[Natural]":
    return MoA.from_array(Array.create_0d(self.array.shape.length))


@register(ctx, MoA._shape)
def _shape(self: MoA[T_box]) -> "MoA[Natural]":
    return MoA.from_array(Array.from_vec(self.array.shape))


# TODO: Implement array indices
@register(ctx, MoA.__getitem__)
def __getitem__(self: MoA[T_box], idxs: "MoA[Natural]") -> "MoA[T_box]":
    n_idxs = idxs.array.shape[Natural(0)]
    new_shape = self.array.shape.drop(n_idxs)

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Natural]) -> T_box:
        return self.array[idxs.array.to_vec().concat(idx)]

    return MoA.from_array(Array.create(new_shape, new_idx_abs))


@register(ctx, MoA.unary_operation)
def unary_operation(self: MoA[T_box], op: Abstraction[T_box, V_box]) -> MoA[V_box]:
    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Natural]) -> V_box:
        return op(self.array[idx])

    return MoA.from_array(Array.create(self.array.shape, new_idx_abs))


# NOTE: This is MoA broadcasting not NumPy broadcasting so dimensions of 1 are not broadcast
@register(ctx, MoA.binary_operation)
def binary_operation(
    self: MoA[T_box],
    op: Abstraction[T_box, Abstraction[U_box, V_box]],
    other: MoA[U_box],
) -> MoA[V_box]:
    dim_difference = self.array.shape.length - other.array.shape.length
    left_shorter = dim_difference.lt(Natural(0))
    res_shape = left_shorter.if_(other.array.shape, self.array.shape)

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Natural]) -> V_box:
        return left_shorter.if_(
            op(self.array[idx.drop(dim_difference * Natural(-1))])(other.array[idx]),
            op(self.array[idx])(other.array[idx.drop(dim_difference)]),
        )

    return MoA.from_array(Array.create(res_shape, new_idx_abs))


@register(ctx, MoA.transpose)
def transpose(self: MoA[T_box]) -> MoA[T_box]:

    new_shape = self.array.shape.reverse()

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Natural]) -> T_box:
        return self.array[idx.reverse()]

    return MoA.from_array(Array.create(new_shape, new_idx_abs))


@register(ctx, MoA.outer_product)
def outer_product(
    self: MoA[T_box],
    op: Abstraction[T_box, Abstraction[U_box, V_box]],
    other: MoA[U_box],
) -> MoA[V_box]:
    l_dim = self.array.shape.length

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Natural]) -> V_box:
        return op(self.array[idx.take(l_dim)])(other.array[idx.drop(l_dim)])

    return MoA.from_array(
        Array.create(self.array.shape.concat(other.array.shape), new_idx_abs)
    )


@register(ctx, MoA.reduce)
def _reduce(
    self: MoA[T_box], op: Abstraction[V_box, Abstraction[T_box, V_box]], initial: V_box
) -> MoA[V_box]:
    return MoA.from_array(Array.create_0d(self.array.to_vec().reduce(initial, op)))


@register(ctx, MoA.gamma)
def gamma(idx: Vec[Natural], shape: Vec[Natural]) -> Natural:
    def loop_abs(val: Natural, i: Natural) -> Natural:
        return idx[i] + (shape[i] * val)

    return shape.length.loop(
        Natural(0), Abstraction.create_bin(loop_abs, Natural(None), Natural(None))
    )
