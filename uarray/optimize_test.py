# import pytest
# import numpy as np

# from .optimize import *


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
