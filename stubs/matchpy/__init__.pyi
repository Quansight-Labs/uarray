import typing

T = typing.TypeVar("T")

class Expression:
    pass

class Symbol(Expression, typing.Generic[T]):
    def __init__(self, name: T): ...
    name: T

class Wildcard(Expression):
    @classmethod
    def dot(cls, name: str) -> "Wildcard": ...
    @classmethod
    def star(cls, name: str) -> "Wildcard": ...
    @classmethod
    def symbol(cls, name: str, symbol: typing.Type[Symbol]) -> "Wildcard": ...

class Constraint: ...

class Pattern:
    def __init__(self, pattern, *constraints: Constraint): ...

class ReplacementRule:
    def __init__(self, pattern: Pattern, replacement: typing.Callable): ...

class ManyToOneReplacer:
    def add(self, rr: ReplacementRule) -> None: ...
    matcher: typing.Any
    def replace(self, expr): ...

class Operation(Expression):
    def __init__(self, *args, **kwargs): ...
    @classmethod
    def new(cls, *args, **kwargs) -> "Operation": ...
    variable_name: str

class Arity:
    def __init__(self, n: int, fixed: bool): ...
