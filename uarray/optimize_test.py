import numpy

from .optimize import *


# @pytest.mark.parametrize(
#     "arr,new_shape",
#     [
#         (np.arange(6, dtype="float64"), (2, 3)),
#         (np.arange(6, dtype="float64"), (3, 2)),
#         (np.array([[1, 2, 3], [4, 5, 6]]).reshape(6), (6,)),
#         # TODO: support -1 in reshape
#     ],
# )
# def test_reshape(arr, new_shape):
#     def fn(a):
#         return a.reshape(new_shape)

#     optimized = optimize(arr.shape)(fn)
#     assert np.array_equal(optimized(arr), fn(arr))


def test_outer_index():
    def outer_index(a, b):
        return numpy.multiply.outer(a, b)[5]

    args = [numpy.arange(10000), numpy.arange(10000)]
    jitted = jit(1, 1)(outer_index)
    assert numpy.array_equal(outer_index(*args), jitted(*args))


def transpose():
    def transpose(a):
        return a.transpose()
    args = [numpy.arange(12).reshape(3, 4)]
    jitted = jit(None)(transpose)
    assert numpy.array_equal(transpose(*args), jitted(*args))
