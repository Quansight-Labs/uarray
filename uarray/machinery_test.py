import matchpy
import typing
from .machinery import *
from .machinery import ManyToOneReplacer, Arg


class TestOperation:
    def test_name(self):
        @operation
        def Op():
            ...

        assert Op.name == "Op"

    def test_empty_arity(self):
        @operation
        def Op():
            ...

        assert Op.args == []
        assert Op.arity == matchpy.Arity(0, True)

    def test_single_arity(self):
        @operation
        def Op(a: int):
            ...

        assert Op.args == [Arg("a", False)]
        assert Op.arity == matchpy.Arity(1, True)

    def test_sequence_arity(self):
        @operation
        def Op(single, *multiple):
            ...

        assert Op.args == [Arg("single", False), Arg("multiple", True)]
        assert Op.arity == matchpy.Arity(1, False)


class TestReplacement:
    def test_no_wildcards(self):
        test_replacer = ManyToOneReplacer()

        @operation
        def A():
            ...

        @operation
        def B():
            ...

        @test_replacer.replacement
        def _a_to_b():
            return lambda: A(), lambda: B()

        assert test_replacer.replace(A()) == B()

    def test_dot_wildcard(self):
        test_replacer = ManyToOneReplacer()

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

        @test_replacer.replacement
        def _c_to_b(x):
            return lambda: C(x), lambda: B()

        assert test_replacer.replace(C(B())) == B()

    def test_star_wildcard(self):
        test_replacer = ManyToOneReplacer()

        @operation
        def B():
            ...

        @operation
        def C(x):
            ...

        @operation
        def D(*xs):
            ...

        @test_replacer.replacement
        def _d_to_b(xs: typing.Sequence):
            return lambda: D(*xs), lambda: B()

        assert test_replacer.replace(D(B(), B())) == B()
        assert test_replacer.replace(C(B())) == C(B())

    def test_star_symbol(self):
        test_replacer = ManyToOneReplacer()

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

        @test_replacer.replacement
        def _d_to_b(e: E):
            return lambda: C(e), lambda: E(e.value() + 1)

        assert test_replacer.replace(C(E(123))) == E(124)
        assert test_replacer.replace(C(A())) == C(A())

    def test_constraint(self):
        class E(Symbol[int]):
            pass

        def constraint(e):
            return e.value() == 5

        class SpecificE(E):
            pass

        SpecificE.constraint = matchpy.CustomConstraint(constraint)

        test_replacer = ManyToOneReplacer()

        @test_replacer.replacement
        def _(e: SpecificE):
            return lambda: e, lambda: E(20)

        assert test_replacer.replace(E(10)) == E(10)
        assert test_replacer.replace(E(5)) == E(20)


class TestOperationAndReplacment:
    def test_works(self):
        test_replacer = ManyToOneReplacer()

        @operation
        def B(x, y):
            ...

        @operation
        def C():
            ...

        @test_replacer.operation_and_replacement
        def A(x, y):
            return B(x, y)

        assert test_replacer.replace(A(C(), C())) == B(C(), C())
