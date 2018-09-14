import typing

import hypothesis

from uarray import PythonArray, Shape, ToPythonArray, replacer, MoaConcatVector

name_strategy = hypothesis.strategies.just("_")
item_strategy = hypothesis.strategies.integers()


def data_strategy(shape: typing.Tuple[int, ...]):
    if not shape:
        return item_strategy
    dim, *rest = shape
    return hypothesis.strategies.tuples(
        *[data_strategy(tuple(rest)) for _ in range(dim)]
    )


hypothesis.strategies.register_type_strategy(
    PythonArray,
    hypothesis.extra.numpy.array_shapes()
    .flatmap(
        lambda shape: hypothesis.strategies.tuples(
            name_strategy, hypothesis.strategies.just(shape), data_strategy(shape)
        )
    )
    .map(lambda a: PythonArray(*a)),
)


@hypothesis.given(pa=hypothesis.infer)
def test_to_python_array_indentity(pa: PythonArray):
    assert replacer.replace(ToPythonArray(pa)).as_tuple == pa.as_tuple


@hypothesis.given(pa=hypothesis.infer)
def test_to_python_array_shape(pa: PythonArray):
    assert replacer.replace(ToPythonArray(Shape(pa))).as_tuple == (
        (len(pa.shape),),
        pa.shape,
    )


@hypothesis.given(pa_l=hypothesis.infer, pa_r=hypothesis.infer)
def test_to_python_array_moa_concat_vector(pa_l: PythonArray, pa_r: PythonArray):
    hypothesis.assume(pa_l.is_vector)
    hypothesis.assume(pa_r.is_vector)

    assert replacer.replace(ToPythonArray(MoaConcatVector(pa_l, pa_r))).as_tuple == (
        ((pa_l.shape[0] + pa_r.shape[0]),),
        pa_l.data + pa_r.data,
    )
