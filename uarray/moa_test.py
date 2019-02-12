import operator
import typing

import pytest

from .core import *
from .core.arrays_test import assert_arrays_eql
from .core.vectors_test import assert_vector_is_list
from .dispatch import *
from .moa import *


def sum_array(shape: Vec[Natural]) -> MoA[Natural]:
    """
    Returns an array whose contents are the sum of those indices.
    """

    @Array.create_idx_abs
    def idx_abs(idx: Vec[Natural]) -> Natural:
        return idx.reduce_fn(Natural(0), operator.add)

    return MoA.from_array(Array.create(shape, idx_abs))


def test_sum_array():
    a = sum_array(Vec.create_infer(Natural(1), Natural(2), Natural(3)))
    assert_arrays_eql(
        a.array,
        (1, 2, 3),
        (((Natural(0), Natural(1), Natural(2)), (Natural(1), Natural(2), Natural(3))),),
    )


def test_index():
    shape = (1, 2, 3)
    idx = (0, 1)

    a = sum_array(Vec.create_infer(*map(Natural, shape)))
    idx_array = MoA.from_array(Array.create_1d(Natural(), *map(Natural, idx)))
    assert_arrays_eql(a[idx_array].array, (3,), (Natural(1), Natural(2), Natural(3)))


def vector(*xs: int) -> Vec[Natural]:
    return Vec.create_infer(*map(Natural, xs))


# def create_test_array(*shape: int) -> ArrayType[typing.Any]:
#     return Array.create(Vec.create_args(Natural(), *shape), variable("idx"))


def row_major_gamma(idx: typing.Tuple[int, ...], shape: typing.Tuple[int, ...]) -> int:
    """
    As defined in 3.30
    """
    assert len(idx) == len(shape)
    if not idx:
        return 0
    assert idx < shape
    return idx[-1] + (shape[-1] * row_major_gamma(idx[:-1], shape[:-1]))


def product(xs: typing.Sequence[int]) -> int:
    p = 1
    for x in xs:
        p *= x
    return p


def row_major_gamma_inverse(
    n: int, shape: typing.Sequence[int]
) -> typing.Tuple[int, ...]:
    """
    As defined in 3.41
    """
    assert n >= 0
    assert n < product(shape)
    for x_ in shape:
        assert x_ > 0

    if not shape:
        return ()

    if len(shape) == 1:
        return (n,)

    *next_shape, dim = shape
    return (*row_major_gamma_inverse(n // dim, next_shape), n % dim)


# def row_major_gamma_inverse_other(
#     n: int, shape: typing.Sequence[int]
# ) -> typing.Tuple[int, ...]:
#     assert n >= 0
#     assert n < product(shape)
#     for x_ in shape:
#         assert x_ > 0

#     res = ()

#     for i in range(len(shape)):
#         res = (i % n)+ res
#     if not shape:
#         return ()

#     if len(shape) == 1:
#         return (n,)

#     *next_shape, dim = shape
#     return (*row_major_gamma_inverse(n // dim, next_shape), n % dim)


@pytest.mark.parametrize(
    "shape,idx,res",
    [
        ((), (), 0),
        ((2, 2), (0, 0), 0),
        ((2, 2), (0, 1), 1),
        ((2, 2), (1, 0), 2),
        ((2, 2), (1, 1), 3),
        ((1, 3, 2), (0, 0, 0), 0),
        ((1, 3, 2), (0, 0, 1), 1),
        ((1, 3, 2), (0, 1, 0), 2),
        ((1, 3, 2), (0, 1, 1), 3),
        ((1, 3, 2), (0, 2, 0), 4),
        ((1, 3, 2), (0, 2, 1), 5),
    ],
)
def test_gamma_and_inverse(shape, idx, res):
    assert row_major_gamma(idx, shape) == res
    assert replace(
        MoA.gamma(
            Vec.create_args(Natural(), *map(Natural, idx)),
            Vec.create_args(Natural(), *map(Natural, shape)),
        )
    ) == Natural(res)

    assert row_major_gamma_inverse(res, shape) == idx
    assert replace(
        MoA.gamma_inverse(
            Natural(res), Vec.create_args(Natural(), *map(Natural, shape))
        )
    ) == Vec.create_args(Natural(), *map(Natural, idx))


# @pytest.mark.parametrize(
#     "shape,idx",
#     [
#         ((), ()),
#         ((10,), (0,)),
#         ((10,), (1,)),
#         ((10,), (9,)),
#         ((2, 3), (1, 2)),
#         ((5, 3, 2), (3, 2, 0)),
#     ],
# )
# def test_ravel(shape: typing.Tuple[int, ...], idx: typing.Tuple[int, ...]):
#     array = create_test_array(*shape)
#     idxed = Index(vector(*idx), array)

#     ravel_idxed = Index(vector(row_major_gamma(idx, shape)), Ravel(array))
#     assert replace(ravel_idxed) == replace(idxed)


@pytest.mark.parametrize(
    "vec,new_shape,idx,value",
    [
        # returns scalars
        ((1,), (), (), 1),
        ((2, 3), (), (), 2),
        # returns vectors
        ((1,), (1,), (0,), 1),
        ((2, 3), (1,), (0,), 2),
        # ((2, 3), (3,), (2,), 2),
        # returns arrays
        # ((0,), (2, 2), (0, 0), 0),
        # ((0,), (2, 2), (0, 1), 0),
        # ((0,), (2, 2), (1, 0), 0),
        # ((0,), (2, 2), (1, 1), 0),
        ((0, 1, 2, 3, 4, 5), (2, 3), (0, 0), 0),
        ((0, 1, 2, 3, 4, 5), (2, 3), (0, 1), 1),
        ((0, 1, 2, 3, 4, 5), (2, 3), (0, 2), 2),
        ((0, 1, 2, 3, 4, 5), (2, 3), (1, 0), 3),
        ((0, 1, 2, 3, 4, 5), (2, 3), (1, 1), 4),
        ((0, 1, 2, 3, 4, 5), (2, 3), (1, 2), 5),
    ],
)
def test_array_from_list_nd(
    vec: typing.Tuple[int, ...],
    new_shape: typing.Tuple[int, ...],
    idx: typing.Tuple[int, ...],
    value: int,
):
    new_s = Array.create_shape(*map(Natural, new_shape))
    reshaped = MoA.from_list_nd(List.create(Natural(), *map(Natural, vec)), new_s)
    assert_vector_is_list(replace(reshaped.array.shape), list(map(Natural, new_shape)))

    i = MoA.from_array(Array.create_1d(Natural(), *map(Natural, idx)))
    idxed = reshaped[i]
    assert replace(idxed.array.to_value()) == Natural(value)


# def all_indices(shape: typing.Tuple[int, ...]) -> typing.Iterable[typing.Iterable[int]]:
#     return itertools.product(*map(range, shape))


# @pytest.mark.parametrize(
#     "original_shape,new_shape",
#     [
#         # normal
#         ((), ()),
#         ((10,), (2, 5)),
#         ((2, 5), (10,)),
#         ((1, 2, 3), (6, 1)),
#         ((1, 2, 3), (1, 6)),
#         ((1, 2, 3), (6,)),
#         # expanding access
#         ((), (10,)),
#         ((), (1, 2, 3)),
#         ((10, 1), (20,)),
#         ((1, 10), (20, 2)),
#         ((4, 1), (4, 5)),
#         ((5,), (4, 5)),
#         # dropping access
#         ((10,), (2,)),
#         ((10,), ()),
#     ],
# )
# def test_reshape(original_shape, new_shape):
#     array = create_test_array(*original_shape)
#     new_shape_array = vector(*new_shape)
#     reshaped = replace(Reshape(new_shape_array, array))
#     assert replace(Shape(reshaped)) == new_shape_array
#     for new_idx in all_indices(new_shape):
#         flat_idx = row_major_gamma(new_idx, new_shape)
#         old_idx = row_major_gamma_inverse(
#             flat_idx % product(original_shape), original_shape
#         )
#         assert replace(Index(vector(*old_idx), array)) == replace(
#             Index(vector(*new_idx), reshaped)
#         )


def test_paper_example():
    """
    Verifies example from paper
    """

    # We start with two arrays, `A` and `B`.
    A_rav = List(Variable("A_rav"), Natural())
    B_rav = List(Variable("B_rav"), Natural())

    A_shape = B_shape = Array.create_shape(Natural(3), Natural(4))

    A = MoA.from_list_nd(A_rav, A_shape)
    B = MoA.from_list_nd(B_rav, B_shape)

    idx = MoA.from_array(Array.create_1d_infer(Natural(0)))

    expr = (A + B).transpose()[idx]

    # Verify shape is what it should be
    assert_vector_is_list(expr.array.shape, [Natural(3)])

    # Verify contents is equal by indexing with `i`.
    i = Natural(Variable("i"))
    idxed = expr.array[Array.create_shape(i)]
    correct_idxed = A_rav[Natural(4) * i] + B_rav[Natural(4) * i]
    assert replace(correct_idxed) == replace(idxed)
