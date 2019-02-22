import math

import hypothesis
from udispatch import *

from .abstractions import *
from .booleans import *
from .naturals import *


@hypothesis._strategies.defines_strategy
def natural_ints(min_value=0, max_value=5):
    return hypothesis.strategies.integers(min_value, max_value)


@hypothesis._strategies.defines_strategy
def naturals():
    return natural_ints().map(Natural)


@hypothesis.given(natural_ints(), natural_ints())
def test_lte(l: int, r: int):
    assert replace(Natural(l).lte(Natural(r))) == Bool(l <= r)


@hypothesis.given(natural_ints(), natural_ints())
def test_add(l: int, r: int):
    assert replace(Natural(l) + Natural(r)) == Natural(l + r)


@hypothesis.given(natural_ints(), natural_ints())
def test_subtract(l: int, r: int):
    assert replace(Natural(l) - Natural(r)) == Natural(l - r)


@hypothesis.given(natural_ints())
def test_loop(n: int):
    def factorial_fn(acc: Natural, idx: Natural) -> Natural:
        return acc * (idx + Natural(1))

    factorial_abs = Abstraction.create_bin(factorial_fn, Natural(), Natural())
    assert replace(Natural(n).loop(Natural(1), factorial_abs)) == Natural(math.factorial(n))
