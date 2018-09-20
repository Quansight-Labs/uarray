# import typing
# import itertools
# import hypothesis

# import uarray

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

