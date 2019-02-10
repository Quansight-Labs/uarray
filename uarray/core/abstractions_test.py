import hypothesis

from .abstractions import *
from ..dispatch import *


@hypothesis._strategies.defines_strategy
def box():
    return hypothesis.strategies.builds(str).map(lambda s: type(s, (Box,), {}))


@hypothesis._strategies.defines_strategy
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
        assert abstr.rettype.rettype == Box(None)

        assert replace(abstr(x)(y)) == Box(Operation("dummy", (x, y)))

    @hypothesis.given(expression())
    def test_apply_returns_abstraction(self, x):
        """
        Checks abstraction that returns abstraction
        """
        abstr = Abstraction.create(lambda x: Box(Operation("inner", (x,))), Box(None))
        abstr_wrapped = Abstraction.create(
            lambda x: Box(Operation("outer", (abstr(x),))), Box(None)
        )
        assert replace(abstr_wrapped(x)) == Box(
            Operation("outer", (Box(Operation("inner", (x,))),))
        )


class TestNaturaliveAbstraction:
    @hypothesis.given(expression(), expression())
    def test_applies_conditionally(self, right_box, wrong_box):
        def fn(a):
            return Box(Operation("inner", (a,)))

        def can_call(a, right_box=right_box):
            return a == right_box

        fn_abs = Abstraction.create_native(fn, can_call, Box(None))

        assert replace(fn_abs(right_box)) == Box(Operation("inner", (right_box,)))
        assert replace(fn_abs(wrong_box)) == fn_abs(wrong_box)

    # @hypothesis.given(expression(), expression())
    def test_nary_no_args(self):
        def fn():
            return Box(Operation("inner", ()))

        fn_abs = Abstraction.create_nary_native(fn, Box(None))

        assert replace(fn_abs) == Box(Operation("inner", ()))

    @hypothesis.given(expression(), expression())
    def test_nary_one_arg(self, right_box, wrong_box):
        def fn(a):
            return Box(Operation("inner", (a,)))

        def can_call(a, right_box=right_box):
            return a == right_box

        fn_abs = Abstraction.create_nary_native(fn, Box(None), can_call)

        assert replace(fn_abs(right_box)) == Box(Operation("inner", (right_box,)))
        assert replace(fn_abs(wrong_box)) == fn_abs(wrong_box)

    @hypothesis.given(expression(), expression())
    def test_nary_two_args(self, first, second):
        def fn(a, b):
            return Box(Operation("inner", (a, b)))

        def can_call_first(a, first=first):
            return a == first

        def can_call_second(b, second=second):
            return b == second

        fn_abs = Abstraction.create_nary_native(
            fn, Box(None), can_call_first, can_call_second
        )

        assert replace(fn_abs(first)(second)) == Box(
            Operation("inner", (first, second))
        )
        assert replace(fn_abs(first)(first)) == replace(fn_abs(first))(first)
        assert replace(fn_abs(second)(first)) == fn_abs(second)(first)
        assert replace(fn_abs(second)(second)) == fn_abs(second)(second)


class TestRenameVariables:
    @hypothesis.given(box())
    def test_rename_variables(self, some_box):
        assert rename_variables(
            Abstraction.create(lambda x: x, some_box(None))
        ) == rename_variables(Abstraction.create(lambda x: x, some_box(None)))


class TestηReduction:
    @hypothesis.given(box(), box())
    def test_η_nested(self, inner_box, outer_box):
        """
        Checks abstraction that returns abstraction

            lambda x: (lambda y: (y,))(x) ==
            lambda x: (x,)
        """
        abstr = Abstraction.create(
            lambda x: outer_box(Operation("inner", (x,))), inner_box(None)
        )
        abstr_wrapped = Abstraction.create(lambda x: abstr(x), inner_box(None))
        assert rename_variables(replace(abstr_wrapped)) == rename_variables(abstr)

    @hypothesis.given(box(), box())
    def test_η_nested_body(self, inner_box, outer_box):
        """
        Check abstraction that returns abstraction,
        where body of abstraction has outer argument in it.
            lambda x: (lambda y: (x, y))(x) ==
            lambda x: (x, x)
        """
        abstr_wrapped = Abstraction.create(
            lambda x: Abstraction.create(
                lambda y: outer_box(Operation("inner", (x, y))), inner_box(None)
            )(x),
            inner_box(None),
        )
        assert rename_variables(replace(abstr_wrapped)) == rename_variables(
            Abstraction.create(
                lambda x: outer_box(Operation("inner", (x, x))), inner_box(None)
            )
        )

    @hypothesis.given(box())
    def test_η_nested_other_type(self, value_box):
        """
        Check abstraction that returns other type of abstraction.

            lambda a: some_fn(a) ==
            always_1
        """
        fn = Abstraction.create_native(
            lambda a: NotImplemented, lambda a: False, value_box(None)
        )
        abstr_wrapped = Abstraction.create(lambda x: fn(x), value_box(None))

        assert replace(abstr_wrapped) == fn

    def test_η_different_var(self):
        """
        Make sure that when we are replacing, if variable is different,
        should not be replaced.

        This shouldn't be simmplified:

            lambda y: lambda x: fn(y)

        But this one should:

            lambda y: lambda x: fn(x)
            = lambda y: fn

        """
        fn = Abstraction.create_native(
            lambda a: NotImplemented, lambda a: False, Box(None)
        )

        # should be simplified
        abstr = Abstraction.create(
            lambda y: Abstraction.create(lambda x: fn(x), Box(None)), Box(None)
        )
        assert rename_variables(replace(abstr)) == rename_variables(
            Abstraction.create(lambda y: fn, Box(None))
        )

        # shouldnt be simplified
        abstr = Abstraction.create(
            lambda y: Abstraction.create(lambda x: fn(y), Box(None)), Box(None)
        )
        assert rename_variables(replace(abstr)) == rename_variables(abstr)
