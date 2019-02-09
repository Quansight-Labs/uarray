import math

import hypothesis

from .abstractions import *
from .booleans import *
from .naturals import *
from ..dispatch import replace


@hypothesis.strategies.defines_strategy
def natural_ints(min_value=0, max_value=5):
    return hypothesis.strategies.integers(min_value, max_value)


@hypothesis.strategies.defines_strategy
def naturals():
    return natural_ints().map(Nat)


@hypothesis.given(natural_ints(), natural_ints())
def test_lte(l: int, r: int):
    assert replace(Nat(l).lte(Nat(r))) == Bool(l <= r)


@hypothesis.given(natural_ints(), natural_ints())
def test_add(l: int, r: int):
    assert replace(Nat(l) + Nat(r)) == Nat(l + r)


@hypothesis.given(natural_ints(), natural_ints())
def test_subtract(l: int, r: int):
    assert replace(Nat(l) - Nat(r)) == Nat(l - r)


@hypothesis.given(natural_ints())
def test_loop(n: int):
    def factorial_fn(acc: Nat, idx: Nat) -> Nat:
        return acc * (idx + Nat(1))

    factorial_abs = Abstraction.create_bin(factorial_fn, Nat(None), Nat(None))
    assert replace(Nat(n).loop(Nat(1), factorial_abs)) == Nat(math.factorial(n))
