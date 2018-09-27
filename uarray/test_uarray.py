# import typing
# import itertools
import pytest
import hypothesis
import hypothesis.extra.numpy
import hypothesis.strategies

import uarray


shape = hypothesis.strategies.shared(
    hypothesis.extra.numpy.array_shapes(min_dims=1), key="_"
)


def shape_to_n(shape_):
    return hypothesis.strategies.integers(
        min_value=0, max_value=uarray.product(shape_) - 1
    )


def test_row_major_gamma():
    assert uarray.row_major_gamma((0, 1, 0), (2, 2, 1)) == 1


@pytest.mark.parametrize(
    "n,shape_,expected",
    [
        (0, (2, 2), (0, 0)),
        (1, (2, 2), (0, 1)),
        (2, (2, 2), (1, 0)),
        (3, (2, 2), (1, 1)),
        (0, (2, 2, 1), (0, 0, 0)),
        (1, (2, 2, 1), (0, 1, 0)),
        (2, (2, 2, 1), (1, 0, 0)),
        (3, (2, 2, 1), (1, 1, 0)),
    ],
)
def test_row_major_gamma_inverse(n, shape_, expected):
    assert uarray.row_major_gamma_inverse(n, shape_) == expected


@hypothesis.given(x=shape, n=shape.flatmap(shape_to_n))
def test_row_major_gamma_3_40(x, n):
    """
    eq. 3.40
    """
    assert uarray.row_major_gamma(uarray.row_major_gamma_inverse(n, x), x) == n


# def data_strategy(shape: typing.Tuple[int, ...]):
#     if not shape:
#         return item_strategy
#     dim, *rest = shape
#     return hypothesis.strategies.tuples(
#         *[data_strategy(tuple(rest)) for _ in range(dim)]
#     )


# tuple_array = hypothesis.extra.numpy.array_shapes().flatmap(
#     lambda shape: hypothesis.strategies.tuples(
#         hypothesis.strategies.just(shape), data_strategy(shape)
#     )
# )

# @hypothesis(tuple_array)
# def test_tuple_shape(x):
#     a = uarray.FromTuple(uarray.Scalar(x))
#      uarray.ToTuple(uarray.Shape(a))

# name_strategy = hypothesis.strategies.just("_")
# item_strategy = hypothesis.strategies.integers()


# @hypothesis.given(pa=hypothesis.infer)
# def test_to_python_array_indentity(pa: PythonArray):
#     assert replacer.replace(ToPythonArray(pa)).as_tuple == pa.as_tuple


# @hypothesis.given(pa=hypothesis.infer)
# def test_to_python_array_shape(pa: PythonArray):
#     assert replacer.replace(ToPythonArray(Shape(pa))).as_tuple == (
#         (len(pa.shape),),
#         pa.shape,
#     )


# @hypothesis.given(pa_l=hypothesis.infer, pa_r=hypothesis.infer)
# def test_to_python_array_moa_concat_vector(pa_l: PythonArray, pa_r: PythonArray):
#     hypothesis.assume(pa_l.is_vector)
#     hypothesis.assume(pa_r.is_vector)

#     assert replacer.replace(ToPythonArray(MoaConcatVector(pa_l, pa_r))).as_tuple == (
#         ((pa_l.shape[0] + pa_r.shape[0]),),
#         pa_l.data + pa_r.data,
#     )

# def indices_from_shape(shape):
#     return itertools.product(map(range, shape))

# @hypothesis.given(tuple_array, tuple_array)
# def test_moa_outer_product(a, b):
#     res = replace(ToTuples(OuterProduct(FromTuples(Scalar(a)), FromTuples(Scalar(b)))))
#     assert isinstance(res, Scalar)
#     shape, data = res.value
#     assert shape = a[0] + b[0]
#     for idx in indices_from_shape(shape):
