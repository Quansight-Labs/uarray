# import typing

# from ..dispatch import *
# from .context import *


# T_box = typing.TypeVar("T_box", bound=Box)
# U_box = typing.TypeVar("U_box", bound=Box)
# T_box_cov = typing.TypeVar("T_box_cov", bound=Box, covariant=True)
# U_box_cov = typing.TypeVar("U_box_cov", bound=Box, covariant=True)


# class Pair(Box, typing.Generic[T_box_cov, U_box_cov]):
#     @classmethod
#     def create(cls, left: T_box, right: U_box) -> "Pair[T_box, U_box]":
#         return cls(Operation(Pair, (left, right)))

#     @property
#     def left(self) -> "T_box_cov":
#         return cls(Operation(Pair.left, (self,)))

#     @property
#     def right(self) -> "U_box_cov":
#         return cls(Operation(Pair.right, (self,)))
