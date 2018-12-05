#%%%
import ast
import numpy
import inspect
import typing
import collections


def create_array(shape: typing.Sequence[typing.Any], a: typing.Any):
    return numpy.array(shape)


print(int.__origin__ is collections.abc.Sequence)

# print(
#     issubclass(
#         inspect.signature(create_array).parameters["shape"].annotation, typing.Sequence
#     )
# )

