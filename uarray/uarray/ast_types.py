import ast
from .core_types import Category


class CStatement(Category):
    name: ast.AST


class CIdentifier(Category):
    name: str
