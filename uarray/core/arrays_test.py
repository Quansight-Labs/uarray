import itertools
import typing

import hypothesis

from ..machinery import replace
from .abstractions import *
from .arrays import *
from .lists import *
from .naturals import *
from .naturals_test import naturals
from .pairs import *
from .vectors import *
from .vectors_test import assert_vector_is_list, list_of_naturals


def assert_arrays_eql(array: ArrayType, shape: typing.List[int], content):
    array = replace(array)
    assert_vector_is_list(replace(Exl(array)), list(map(nat, shape)))  # type: ignore
    idx_abs = replace(Exr(array))
    for indxs in itertools.product(*map(range, shape)):
        x = content
        for i in indxs:
            x = x[i]
        assert replace(Apply(idx_abs, list_(*map(nat, indxs)))) == x


@hypothesis.given(naturals())
def test_0d_array(x):
    assert_arrays_eql(array_0d(x), [], x)


@hypothesis.given(list_of_naturals())
def test_1d_array(xs):
    assert_arrays_eql(array_1d(*xs), [len(xs)], xs)


@hypothesis.given(list_of_naturals())
def test_vec_to_array(xs):
    assert_arrays_eql(VecToArray1D(vec(*xs)), [len(xs)], xs)


@hypothesis.given(list_of_naturals())
def test_array_to_vec(xs):
    assert_vector_is_list(Array1DToVec(array_1d(*xs)), xs)
