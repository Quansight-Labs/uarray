import typing
import dataclasses
import matchpy

T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")
RET = typing.TypeVar("RET")
ARG1 = typing.TypeVar("ARG1")
ARG2 = typing.TypeVar("ARG2")


class Type:
    """
    Just for compile time checking with MyPy
    """

    pass


class ArrayType(Type, typing.Generic[T]):
    """
    mapping from indices to T
    """

    pass


class NatType(Type):
    """
    Natural number
    """

    pass


class CallableUnaryType(Type, typing.Generic[RET, ARG1]):
    pass


class CallableBinaryType(Type, typing.Generic[RET, ARG1, ARG2]):
    pass


class VectorType(Type, typing.Generic[T]):
    """
    List with length
    """

    pass


# class BoundedNatType(Type):
#     pass


ShapeType = VectorType[NatType]


ListType = CallableUnaryType[T, NatType]
IndicesType = ListType[NatType]
ArrayIndexType = CallableUnaryType[T, IndicesType]


TYPE = typing.TypeVar("TYPE", bound=Type)
