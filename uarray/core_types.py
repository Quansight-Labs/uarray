import typing

T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")
RET = typing.TypeVar("RET")
ARG1 = typing.TypeVar("ARG1")
ARG2 = typing.TypeVar("ARG2")


class Category:
    """
    Just for compile time checking with mypy
    """

    pass


class CNestedSequence(Category):
    pass


class CNDArray(Category):
    pass


class CContent(Category):
    pass


class CUnbound(Category):
    pass


class CCallableUnary(Category, typing.Generic[RET, ARG1]):
    pass


class CCallableBinary(Category, typing.Generic[RET, ARG1, ARG2]):
    pass


CGetItem = CCallableUnary[CNestedSequence, CContent]

class CUnboundContent(CUnbound, CContent):
    pass


class CInt(CContent):
    name: int


CVector = CCallableUnary[T, CContent]

CIndexFn = CCallableUnary[CContent, CVector[CContent]]
