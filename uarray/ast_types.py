import typing
import ast
from .core_types import (
    CNestedSequence,
    CContent,
    Category,
    CUnbound,
    CCallableUnary,
    CVector,
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


class CInitializableArray(CInitializable, CNestedSequence):
    pass


CStatements = CVector[CStatement]
CInitializer = CCallableUnary[CStatements, CIdentifier]


class CExpression(CInitializer):
    name: ast.AST


class CSubstituteIdentifier(CInitializer):
    name: typing.Callable[[CIdentifier], CStatements]


class CSubstituteStatements(CCallableUnary[CStatements, CStatements]):
    name: typing.Callable[[CStatements], CStatements]


class CFunctionReturnsStatements(Category):
    pass
