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
        shape = Vector(Int(0), List())
        psi = Always(Int(0))
        arr = Array(shape, psi)
        assert replace(ArrayShape(arr)) == shape

    def test_psi(self):
        shape = Vector(Int(0), List())
        psi = Always(Int(0))
        arr = Array(shape, psi)
        assert replace(ArrayIndex(arr)) == psi


class TestAlways:
    def test_returns_val(self):
        val = Int(333)
        arg = Int(123)
        return replace(ApplyUnary(Always(val), arg)) == val


class TestCompose:
    def test_returns_composition(self):
        @operation
        def DoubleCallable() -> CallableUnaryType[NatType, NatType]:
            ...

        @replacement
        def _call_double_int(i: Int) -> ThunkPairType[NatType]:
            return lambda: ApplyUnary(DoubleCallable(), i), lambda: Int(i.value() * 2)

        @operation
        def IncCallable() -> CallableUnaryType[NatType, NatType]:
            ...

        @replacement
        def _call_incr_int(i: Int) -> ThunkPairType[NatType]:
            return lambda: ApplyUnary(IncCallable(), i), lambda: Int(i.value() + 1)

        val = Int(5)

        assert replace(
            ApplyUnary(Compose(DoubleCallable(), IncCallable()), val)
        ) == Int((5 + 1) * 2)
        assert replace(
            ApplyUnary(Compose(IncCallable(), DoubleCallable()), val)
        ) == Int((5 * 2) + 1)


class TestPythonUnaryFunction:
    def test_unwraps(self):
        def inc_int(i: Int) -> Int:
            return Int(i.value() + 1)

        c = PythonUnaryFunction(inc_int)
        assert replace(ApplyUnary(c, Int(2))) == Int(3)


class TestList:
    def test_list_first(self):
        assert replace(ListFirst(List(Int(0), Int(1), Int(2)))) == Int(0)

    def test_list_push(self):
        assert replace(ListPush(Int(-1), List(Int(0), Int(1), Int(2)))) == List(
            Int(-1), Int(0), Int(1), Int(2)
        )

    def test_list_concat(self):
        assert replace(ListConcat(List(Int(0), Int(1)), List(Int(2), Int(3)))) == List(
            Int(0), Int(1), Int(2), Int(3)
        )


class TestVector:
    def test_to_array(self):
        res = VectorToArray(Vector(Int(2), List(Int(0), Int(1))))

        assert replace(ArrayShape(res)) == Vector(Int(1), List(Int(2)))
        assert replace(ApplyUnary(ArrayIndex(res), List(Int(0)))) == Int(0)
        assert replace(ApplyUnary(ArrayIndex(res), List(Int(1)))) == Int(1)
