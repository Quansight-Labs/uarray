import typing

RET = typing.TypeVar("RET")
ARG1 = typing.TypeVar("ARG1")
ARG2 = typing.TypeVar("ARG2")


class CArray:
    pass


class CContent:
    pass


class CUnbound:
    pass


class CCallableUnary(typing.Generic[RET, ARG1]):
    pass


class CCallableBinary(typing.Generic[RET, ARG1, ARG2]):
    pass


CGetItem = CCallableUnary[CArray, CContent]


class CUnboundContent(CUnbound, CContent):
    ...


class CInt(CContent):
    name: int
