# import typing
# import pytest

# from .numpy import *


# # examples from https://docs.scipy.org/doc/numpy-1.15.0/user/basics.broadcasting.html#general-broadcasting-rules
# @pytest.mark.parametrize(
#     "shape1,shape2,res_shape",
#     [
#         ((256, 256, 3), (3,), (256, 256, 3)),
#         ((8, 1, 6, 1), (7, 1, 5), (8, 7, 6, 5)),
#         ((5, 4), (1,), (5, 4)),
#         ((5, 4), (4,), (5, 4)),
#         ((15, 3, 5), (15, 1, 5), (15, 3, 5)),
#         ((15, 3, 5), (3, 5), (15, 3, 5)),
#         ((15, 3, 5), (3, 1), (15, 3, 5)),
#         ((3,), (4,), None),
#         ((2, 1), (8, 4, 3), None),
#     ],
# )
# def test_broadcast_shapes(shape1, shape2, res_shape):
#     res = BroadcastShapes(GetItem(vector(*shape1)), GetItem(vector(*shape2)))
#     if res_shape is not None:
#         intended_res = GetItem(vector(*res_shape))
#         assert replace(res) == replace(intended_res)
#     else:
#         with pytest.raises(ValueError):
#             replace(res)
