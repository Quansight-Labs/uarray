import hypothesis

from ..dispatch import *
from .abstractions import *


@hypothesis.strategies.defines_strategy
def expression():
    return hypothesis.strategies.builds(object).map(Box)


class TestAbstraction:
    @hypothesis.given(expression(), expression())
    def test_apply_itself(self, x, y):
        res = Abstraction.create(lambda _: x, Box(None))(y)
        assert replace(res) == x

    @hypothesis.given(expression())
    def test_apply_arg(self, y):
        assert replace(Abstraction.create(lambda x: x, Box(None))(y)) == y

    @hypothesis.given(expression())
    def test_apply_replaces_inner(self, y):
        assert replace(
            Abstraction.create(lambda x: Box(Operation("dummy", (x,))), Box(None))(y)
        ) == Box(Operation("dummy", (y,)))

    @hypothesis.given(expression(), expression())
    def test_applies_only_outer(self, x, y):
        """
        Verifies that variable is different each time
        """
        abstr = Abstraction.create(
            lambda arg1: Abstraction.create(
                lambda arg2: Box(Operation("dummy", (arg1, arg2))), Box(None)
            ),
            Box(None),
        )
        assert replace(abstr(x)(y)) == Box(Operation("dummy", (x, y)))
