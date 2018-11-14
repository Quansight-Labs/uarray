import typing
import pytest

from .moa import *


def create_test_array(*shape: int) -> CArray:
    return with_shape(typing.cast(CArray, unbound()), [Int(s) for s in shape])


def row_major_gamma(idx, shape):
    """
    As defined in 3.30
    """
    assert len(idx) == len(shape)
    if not idx:
        return 0
    assert idx < shape
    return idx[-1] + (shape[-1] * row_major_gamma(idx[:-1], shape[:-1]))


# def row_major_gamma_inverse(n, shape):
#     """
#     As defined in 3.41
#     """
#     assert n >= 0
#     assert n < product(shape)
#     for x_ in shape:
#         assert x_ > 0

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
    ],
)
def test_gamma(shape, idx, res):
    assert row_major_gamma(idx, shape) == res


@pytest.mark.parametrize(
    "shape,idx",
    [
        ((), ()),
        ((10,), (0,)),
        ((10,), (1,)),
        ((10,), (9,)),
        ((2, 3), (1, 2)),
        ((5, 3, 2), (3, 2, 0)),
    ],
)
def test_ravel(shape, idx):
    array = create_test_array(*shape)
    idxed = Index(vector(*idx), array)

    ravel_idxed = Index(vector(row_major_gamma(idx, shape)), Ravel(array))
    assert replace(ravel_idxed) == replace(idxed)


@pytest.mark.parametrize(
    "vec,new_shape,idx,value",
    [
        # returns scalars
        ((1,), (), (), 1),
        ((2, 3), (), (), 2),
        # returns vectors
        ((1,), (1,), (0,), 1),
        ((2, 3), (1,), (0,), 2),
        ((2, 3), (3,), (2,), 2),
        # returns arrays
        ((0,), (2, 2), (0, 0), 0),
        ((0,), (2, 2), (0, 1), 0),
        ((0,), (2, 2), (1, 0), 0),
        ((0,), (2, 2), (1, 1), 0),
        ((0, 1, 2, 3, 4, 5), (2, 3), (0, 0), 0),
        ((0, 1, 2, 3, 4, 5), (2, 3), (0, 1), 1),
        ((0, 1, 2, 3, 4, 5), (2, 3), (0, 2), 2),
        ((0, 1, 2, 3, 4, 5), (2, 3), (1, 0), 3),
        ((0, 1, 2, 3, 4, 5), (2, 3), (1, 1), 4),
        ((0, 1, 2, 3, 4, 5), (2, 3), (1, 2), 5),
    ],
)
def test_reshape_vector(vec, new_shape, idx, value):
    v = vector(*vec)
    new_s = vector(*new_shape)
    s = GetItem(new_s)
    reshaped = ReshapeVector(s, v)
    assert replace(Shape(reshaped)) == new_s
    i = vector(*idx)
    idxed = Index(i, reshaped)
    assert replace(idxed) == Scalar(Int(value))
