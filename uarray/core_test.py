import itertools
import typing

import pytest

from .core import *


class TestInt:
    def test_int_has_integer_value(self):
        assert Int(123).value() == 123

    def test_int_is_natural(self):
        i: NatType = Int(123)


class TestArray:
    def test_shape(self):
        shape = Vector()
        psi = Always(Zero())
        arr = Array(shape, psi)
        assert replace(Shape(arr)) == shape

    def test_psi(self):
        shape = Vector()
        psi = Always(Zero())
        arr = Array(shape, psi)
        assert replace(Psi(arr)) == psi


class TestAlways:
    def test_returns_val(self):
        val = Int(333)
        arg = Int(123)
        return replace(CallUnary(Always(val), arg)) == val


class TestCompose:
    def test_returns_composition(self):
        @operation
        def DoubleCallable() -> CallableUnaryType[NatType, NatType]:
            ...

        @replacement
        def _call_double_int(i: Int) -> Pair[NatType]:
            return lambda: CallUnary(DoubleCallable(), i), lambda: Int(i.value() * 2)

        @operation
        def IncCallable() -> CallableUnaryType[NatType, NatType]:
            ...

        @replacement
        def _call_incr_int(i: Int) -> Pair[NatType]:
            return lambda: CallUnary(IncCallable(), i), lambda: Int(i.value() + 1)

        val = Int(5)

        assert replace(CallUnary(Compose(DoubleCallable(), IncCallable()), val)) == Int(
            (5 + 1) * 2
        )
        assert replace(CallUnary(Compose(IncCallable(), DoubleCallable()), val)) == Int(
            (5 * 2) + 1
        )
