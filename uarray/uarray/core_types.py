import typing

RET = typing.TypeVar("RET")
ARG1 = typing.TypeVar("ARG1")
ARG2 = typing.TypeVar("ARG2")


class Category:
    """
    Just for compile time checking with mypy
    """
    pass

class CArray(Category):
    pass


class CContent(Category):
    pass


class CUnbound(Category):
    pass


class CCallableUnary(Category, typing.Generic[RET, ARG1]):
    pass


class CCallableBinary(Category, typing.Generic[RET, ARG1, ARG2]):
    pass


CGetItem = CCallableUnary[CArray, CContent]


class CUnboundContent(CUnbound, CContent):
    ...


class CInt(CContent):
    name: int
