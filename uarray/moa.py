import typing
from .dispatch import *
from .core import *

__all__ = [
    "dim",
    "shape",
    "index",
    "binary_operation_abstraction",
    "binary_op",
    "transpose",
    "reduce",
    "outer_product",
    "gamma",
    "array_from_list_nd",
    "unary_operation_abstraction",
]


ctx = MapChainCallable()

default_context.append(ctx)

T_box = typing.TypeVar("T_box", bound=Box)
U_box = typing.TypeVar("U_box", bound=Box)
V_box = typing.TypeVar("V_box", bound=Box)


def dim(a: Array[T_box]) -> "Array[Nat]":
    return Array(Operation(dim, (a,)), Nat(None))


@register(ctx, dim)
def _dim(a: Array[T_box]) -> "Array[Nat]":
    return Array.create_0d(a.shape.length)


def shape(a: Array[T_box]) -> "Array[Nat]":
    return Array(Operation(shape, (a,)), Nat(None))


@register(ctx, shape)
def _shape(a: Array[T_box]) -> "Array[Nat]":
    return Array.from_vec(a.shape)


# TODO: Implement array indices
def index(idxs: "Array[Nat]", a: Array[T_box]) -> "Array[T_box]":
    return a._replace(Operation(index, (idxs, a)))


@register(ctx, index)
def _index(idxs: "Array[Nat]", a: Array[T_box]) -> "Array[T_box]":
    n_idxs = idxs.shape[Nat(0)]
    new_shape = a.shape.drop(n_idxs)

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Nat]) -> T_box:
        return a[idxs.to_vec().concat(idx)]

    return Array.create(new_shape, new_idx_abs)


def unary_operation_abstraction(
    op: Abstraction[T_box, V_box], a: Array[T_box]
) -> Array[V_box]:
    return Array(Operation(unary_operation_abstraction, (op, a)), op.rettype)


@register(ctx, unary_operation_abstraction)
def _unary_operation_abstraction(
    op: Abstraction[T_box, V_box], a: Array[T_box]
) -> Array[V_box]:
    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Nat]) -> V_box:
        return op(a[idx])

    return Array.create(a.shape, new_idx_abs)


# TODO: Implement broadcasting
def binary_operation_abstraction(
    left: Array[T_box],
    op: Abstraction[T_box, Abstraction[U_box, V_box]],
    right: Array[U_box],
) -> Array[V_box]:
    return Array(
        Operation(binary_operation_abstraction, (left, op, right)), op.rettype.rettype
    )


# NOTE: This is MoA broadcasting not NumPy broadcasting so dimensions of 1 are not broadcast
@register(ctx, binary_operation_abstraction)
def _binary_operation_abstraction(
    left: Array[T_box],
    op: Abstraction[T_box, Abstraction[U_box, V_box]],
    right: Array[U_box],
) -> Array[V_box]:
    dim_difference = left.shape.length - right.shape.length
    left_shorter = dim_difference.lt(Nat(0))
    res_shape = left_shorter.if_(right.shape, left.shape)

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Nat]) -> V_box:
        return left_shorter.if_(
            op(left[idx.drop(dim_difference * Nat(-1))])(right[idx]),
            op(left[idx])(right[idx.drop(dim_difference)]),
        )

    return Array.create(res_shape, new_idx_abs)


def binary_op(
    left: Array[T_box], op: typing.Callable[[T_box, U_box], V_box], right: Array[U_box]
) -> Array[V_box]:
    return binary_operation_abstraction(
        left, Abstraction.create_bin(op, left.dtype, right.dtype), right
    )


# TODO: make work for any ordering
def transpose(a: Array[T_box]) -> Array[T_box]:
    return a._replace(Operation(transpose, (a,)))


@register(ctx, transpose)
def _transpose(a: Array[T_box]) -> Array[T_box]:

    new_shape = a.shape.reverse()

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Nat]) -> T_box:
        return a[idx.reverse()]

    return Array.create(new_shape, new_idx_abs)


def outer_product(
    l: Array[T_box], op: Abstraction[T_box, Abstraction[U_box, V_box]], r: Array[U_box]
) -> Array[V_box]:
    return Array(Operation(outer_product, (l, op, r)), op.rettype.rettype)


@register(ctx, outer_product)
def _outer_product(
    l: Array[T_box], op: Abstraction[T_box, Abstraction[U_box, V_box]], r: Array[U_box]
) -> Array[V_box]:
    l_dim = l.shape.length

    @Array.create_idx_abs
    def new_idx_abs(idx: Vec[Nat]) -> V_box:
        return op(l[idx.take(l_dim)])(r[idx.drop(l_dim)])

    return Array.create(l.shape.concat(r.shape), new_idx_abs)


def reduce(
    a: Array[T_box], op: Abstraction[V_box, Abstraction[T_box, V_box]], initial: V_box
) -> Array[V_box]:
    return Array(Operation(reduce, (a, op, initial)), op.rettype.rettype)


@register(ctx, reduce)
def _reduce(
    a: Array[T_box], op: Abstraction[V_box, Abstraction[T_box, V_box]], initial: V_box
) -> Array[V_box]:
    return Array.create_0d(a.to_vec().reduce(initial, op))


def gamma(idx: Vec[Nat], shape: Vec[Nat]) -> Nat:
    return Nat(Operation(gamma, (idx, shape)))


@register(ctx, gamma)
def _gamma(idx: Vec[Nat], shape: Vec[Nat]) -> Nat:
    def loop_abs(val: Nat, i: Nat) -> Nat:
        return idx[i] + (shape[i] * val)

    return shape.length.loop(
        Nat(0), Abstraction.create_bin(loop_abs, Nat(None), Nat(None))
    )


def array_from_list_nd(lst: List[T_box], shape: Vec[Nat]) -> Array[T_box]:
    """
    Returns a reshaped array
    """
    return Array(Operation(array_from_list_nd, (lst, shape)), lst.dtype)


@register(ctx, array_from_list_nd)
def _array_from_list_nd(lst: List[T_box], shape: Vec[Nat]) -> Array[T_box]:
    @Array.create_idx_abs
    def idx_abs(idx: Vec[Nat]) -> T_box:
        return lst[gamma(idx, shape)]

    return Array.create(shape, idx_abs)
