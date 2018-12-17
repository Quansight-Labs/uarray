import hypothesis
import matchpy

from ..machinery import replace, operation
from .abstractions import *


@hypothesis.strategies.defines_strategy
def expression():
    return hypothesis.strategies.builds(object).map(matchpy.Symbol)


@operation
def DummyOp(x):
    ...


@operation
def DummyOpBin(x, y):
    ...


class TestAbstraction:
    @hypothesis.given(expression(), expression())
    def test_apply_itself(self, x, y):
        assert replace(Apply(abstraction(lambda _: x), y)) == x

    @hypothesis.given(expression())
    def test_apply_arg(self, y):
        assert replace(Apply(abstraction(lambda x: x), y)) == y

    @hypothesis.given(expression())
    def test_apply_replaces_inner(self, y):
        assert replace(Apply(abstraction(lambda x: DummyOp(x)), y)) == DummyOp(y)

    @hypothesis.given(expression(), expression())
    def test_applies_only_outer(self, x, y):
        """
        Verifies that variable is different each time
        """
        abstr = abstraction(
            lambda arg1: abstraction(lambda arg2: DummyOpBin(arg1, arg2))
        )
        assert replace(Apply(Apply(abstr, x), y)) == DummyOpBin(x, y)
