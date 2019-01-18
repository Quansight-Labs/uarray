# import typing
# import pytest

# from .core import *
# from .core.vectors_test import assert_vector_is_list
# from .core.arrays_test import assert_arrays_eql
# from .machinery import *
# from .moa import *


# @operation
# def SumList(length: NatType, l: ListType[NatType]) -> NatType:
#     ...


# @replacement
# def _replace_sum_list(l: ListType[NatType]) -> DoubleThunkType[NatType]:
#     return lambda: SumList(nat(0), l), lambda: nat(0)


# @replacement
# def _replace_sum_list_recur(
#     i: NonZeroInt, l: ListType[NatType]
# ) -> DoubleThunkType[NatType]:
#     return (
#         lambda: SumList(i, l),
#         lambda: NatAdd(ListFirst(l), SumList(NatDecr(i), ListRest(l))),
#     )


# def sum_array(shape: VecType[NatType]):
#     return Pair(shape, abstraction(lambda idxs: SumList(Exl(shape), idxs)))


# def test_sum_array():
#     a = sum_array(vec(nat(1), nat(2), nat(3)))
#     assert_arrays_eql(
#         a, (1, 2, 3), (((nat(0), nat(1), nat(2)), (nat(1), nat(2), nat(3))),)
#     )


# def test_index():
#     shape = (1, 2, 3)
#     idx = (0, 1)
#     a = sum_array(vec(*map(nat, shape)))
#     assert_arrays_eql(
#         Index(array_1d(*map(nat, idx)), a), (3,), (nat(1), nat(2), nat(3))
#     )


# def vector(*xs: int) -> VecType[NatType]:
#     return vec(*map(nat, xs))


# def create_test_array(*shape: int) -> ArrayType[typing.Any]:
#     return Pair(vector(*shape), variable("idx"))


# def row_major_gamma(idx: typing.Tuple[int, ...], shape: typing.Tuple[int, ...]) -> int:
#     """
#     As defined in 3.30
#     """
#     assert len(idx) == len(shape)
#     if not idx:
#         return 0
#     assert idx < shape
#     return idx[-1] + (shape[-1] * row_major_gamma(idx[:-1], shape[:-1]))


# def product(xs: typing.Sequence[int]) -> int:
#     p = 1
#     for x in xs:
#         p *= x
#     return p


# def row_major_gamma_inverse(
#     n: int, shape: typing.Sequence[int]
# ) -> typing.Tuple[int, ...]:
#     """
#     As defined in 3.41
#     """
#     assert n >= 0
#     assert n < product(shape)
#     for x_ in shape:
#         assert x_ > 0

#     if not shape:
#         return ()

#     if len(shape) == 1:
#         return (n,)

#     *next_shape, dim = shape
#     return (*row_major_gamma_inverse(n // dim, next_shape), n % dim)


# @pytest.mark.parametrize(
#     "shape,idx,res",
#     [
#         ((), (), 0),
#         ((2, 2), (0, 0), 0),
#         ((2, 2), (0, 1), 1),
#         ((2, 2), (1, 0), 2),
#         ((2, 2), (1, 1), 3),
#     ],
# )
# def test_gamma(shape, idx, res):
#     assert row_major_gamma(idx, shape) == res


# # @pytest.mark.parametrize(
# #     "shape,idx",
# #     [
# #         ((), ()),
# #         ((10,), (0,)),
# #         ((10,), (1,)),
# #         ((10,), (9,)),
# #         ((2, 3), (1, 2)),
# #         ((5, 3, 2), (3, 2, 0)),
# #     ],
# # )
# # def test_ravel(shape: typing.Tuple[int, ...], idx: typing.Tuple[int, ...]):
# #     array = create_test_array(*shape)
# #     idxed = Index(vector(*idx), array)

# #     ravel_idxed = Index(vector(row_major_gamma(idx, shape)), Ravel(array))
# #     assert replace(ravel_idxed) == replace(idxed)


# @pytest.mark.parametrize(
#     "vec,new_shape,idx,value",
#     [
#         # returns scalars
#         ((1,), (), (), 1),
#         ((2, 3), (), (), 2),
#         # returns vectors
#         ((1,), (1,), (0,), 1),
#         ((2, 3), (1,), (0,), 2),
#         # ((2, 3), (3,), (2,), 2),
#         # returns arrays
#         # ((0,), (2, 2), (0, 0), 0),
#         # ((0,), (2, 2), (0, 1), 0),
#         # ((0,), (2, 2), (1, 0), 0),
#         # ((0,), (2, 2), (1, 1), 0),
#         ((0, 1, 2, 3, 4, 5), (2, 3), (0, 0), 0),
#         ((0, 1, 2, 3, 4, 5), (2, 3), (0, 1), 1),
#         ((0, 1, 2, 3, 4, 5), (2, 3), (0, 2), 2),
#         ((0, 1, 2, 3, 4, 5), (2, 3), (1, 0), 3),
#         ((0, 1, 2, 3, 4, 5), (2, 3), (1, 1), 4),
#         ((0, 1, 2, 3, 4, 5), (2, 3), (1, 2), 5),
#     ],
# )
# def test_reshape_vector(
#     vec: typing.Tuple[int, ...],
#     new_shape: typing.Tuple[int, ...],
#     idx: typing.Tuple[int, ...],
#     value: int,
# ):
#     new_s = vector(*new_shape)
#     reshaped = ListToArrayND(list_(*map(nat, vec)), new_s)
#     assert_vector_is_list(replace(Exl(reshaped)), list(map(nat, new_shape)))

#     i = array_1d(*map(nat, idx))
#     idxed = Index(i, reshaped)
#     assert replace(Array0DToInner(idxed)) == nat(value)


# # def all_indices(shape: typing.Tuple[int, ...]) -> typing.Iterable[typing.Iterable[int]]:
# #     return itertools.product(*map(range, shape))


# # @pytest.mark.parametrize(
# #     "original_shape,new_shape",
# #     [
# #         # normal
# #         ((), ()),
# #         ((10,), (2, 5)),
# #         ((2, 5), (10,)),
# #         ((1, 2, 3), (6, 1)),
# #         ((1, 2, 3), (1, 6)),
# #         ((1, 2, 3), (6,)),
# #         # expanding access
# #         ((), (10,)),
# #         ((), (1, 2, 3)),
# #         ((10, 1), (20,)),
# #         ((1, 10), (20, 2)),
# #         ((4, 1), (4, 5)),
# #         ((5,), (4, 5)),
# #         # dropping access
# #         ((10,), (2,)),
# #         ((10,), ()),
# #     ],
# # )
# # def test_reshape(original_shape, new_shape):
# #     array = create_test_array(*original_shape)
# #     new_shape_array = vector(*new_shape)
# #     reshaped = replace(Reshape(new_shape_array, array))
# #     assert replace(Shape(reshaped)) == new_shape_array
# #     for new_idx in all_indices(new_shape):
# #         flat_idx = row_major_gamma(new_idx, new_shape)
# #         old_idx = row_major_gamma_inverse(
# #             flat_idx % product(original_shape), original_shape
# #         )
# #         assert replace(Index(vector(*old_idx), array)) == replace(
# #             Index(vector(*new_idx), reshaped)
# #         )
