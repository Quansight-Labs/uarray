import typing
import ast
from .core_types import (
    ArrayType,
    CContent,
    Category,
    CUnbound,
    CallableUnaryType,
    CVectorCallable,
)


class CStatement(Category):
    name: ast.AST


class CIdentifier(Category):
    name: str


class CUnboundIdentifier(CIdentifier, CUnbound):
    pass


class CInitializable(Category):
    pass


class CInitializableContent(CInitializable, CContent):
    pass


class CInitializableArray(CInitializable, ArrayType):
    pass


CStatements = CVectorCallable[CStatement]
CInitializer = CallableUnaryType[CStatements, CIdentifier]


class CExpression(CInitializer):
    name: ast.AST


class CSubstituteIdentifier(CInitializer):
    name: typing.Callable[[CIdentifier], CStatements]


class CSubstituteStatements(CallableUnaryType[CStatements, CStatements]):
    name: typing.Callable[[CStatements], CStatements]


class CFunctionReturnsStatements(Category):
    pass
