import ast
import typing

import astunparse
import numpy

from udispatch import *
from uarray import *
from .lazy_ndarray import numpy_ufunc
from .ast import *


def ast_to_source(node: ast.AST) -> str:
    return astunparse.unparse(node)


def ast_source(expr: Box) -> typing.List[str]:
    replaced = replace(to_ast(expr))
    # Verify return type should be the same
    assert replaced.replace(None) == replaced.replace(None)

    assert isinstance(replaced.value, AST)
    return list(map(ast_to_source, list(replaced.value.init) + [replaced.value.get]))


class TestToAST:
    def test_numbers(self):
        assert ast_source(Natural(123)) == ["123\n"]
        assert ast_source(Box(1.2)) == ["1.2\n"]

    def test_vec(self):
        assert ast_source(Vec.create_infer(Natural(123), Natural(456))) == ["(123, 456)\n"]

    def test_ufunc(self):
        assert ast_source(numpy_ufunc(Box(numpy.multiply), Natural(1), Natural(2))) == [
            "numpy.multiply(1, 2)\n"
        ]
