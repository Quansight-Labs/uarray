from .machinery import *


@operation
def A():
    ...


@operation
def B():
    ...


@operation
def C(x):
    ...


@operation
def D(*xs):
    ...


class E(Symbol[int]):
    pass


class TestReplacement:
    def test_no_wildcards(self):
        test_replacer = ManyToOneReplacer()

        @test_replacer.replacement
        def _a_to_b():
            return lambda: A(), lambda: B()

        assert test_replacer.replace(A()) == B()

    def test_dot_wildcard(self):
        test_replacer = ManyToOneReplacer()

        @test_replacer.replacement
        def _c_to_b(x):
            return lambda: C(x), lambda: B()

        assert test_replacer.replace(C(B())) == B()

    def test_star_wildcard(self):
        test_replacer = ManyToOneReplacer()

        @test_replacer.replacement
        def _d_to_b(xs: typing.Sequence):
            return lambda: D(*xs), lambda: B()

        assert test_replacer.replace(D(B(), B())) == B()
        assert test_replacer.replace(C(B())) == C(B())

    def test_star_symbol(self):
        test_replacer = ManyToOneReplacer()

        @test_replacer.replacement
        def _d_to_b(e: E):
            return lambda: C(e), lambda: E(e.value() + 1)

        assert test_replacer.replace(C(E(123))) == E(124)
        assert test_replacer.replace(C(A())) == C(A())
