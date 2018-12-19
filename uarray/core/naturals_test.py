import hypothesis

from ..machinery import replace
from .naturals import *
from .booleans import bool_


@hypothesis.strategies.defines_strategy
def natural_ints(min_value=0, max_value=5):
    return hypothesis.strategies.integers(min_value, max_value)


@hypothesis.strategies.defines_strategy
def naturals():
    return natural_ints().map(nat)


@hypothesis.given(natural_ints())
def test_constructor_is_natural(x: int):
    n: NatType = nat(x)
    assert isinstance(n, NatType)


@hypothesis.given(natural_ints(), natural_ints())
def test_lte(l: int, r: int):
    assert replace(NatLTE(nat(l), nat(r))) == bool_(l <= r)


@hypothesis.given(natural_ints())
def test_incr(x: int):
    assert replace(NatIncr(nat(x))) == nat(x + 1)


@hypothesis.given(natural_ints(1))
def test_decr(x: int):
    assert replace(NatDecr(nat(x))) == nat(x - 1)


@hypothesis.given(natural_ints(), natural_ints())
def test_add(l: int, r: int):
    assert replace(NatAdd(nat(l), nat(r))) == nat(l + r)


@hypothesis.given(natural_ints(), natural_ints())
def test_subtract(l: int, r: int):
    assert replace(NatSubtract(nat(l), nat(r))) == nat(l - r)
