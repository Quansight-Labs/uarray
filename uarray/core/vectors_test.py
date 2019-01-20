import hypothesis
import typing
from ..dispatch import *
from .vectors import *
from .naturals import *
from .naturals_test import naturals, natural_ints
from .abstractions import *

T = typing.TypeVar("T")
T_box = typing.TypeVar("T_box", bound=Box)


@hypothesis.strategies.defines_strategy
def list_of_naturals(min_size=0, max_size=5):
    return hypothesis.strategies.lists(
        elements=naturals(), min_size=min_size, max_size=max_size
    )


def assert_vector_is_list(v: Vec[T_box], xs: typing.Sequence[T]):
    v = replace(v)
    assert replace(v.length) == Nat(len(xs))
    for i, x in enumerate(xs):
        assert replace(v.list[Nat(i)]) == x


@hypothesis.given(list_of_naturals())
def test_constructor_has_length_and_can_get(xs):
    assert_vector_is_list(Vec.create_args(Nat(None), *xs), xs)


@hypothesis.given(list_of_naturals(min_size=1))
def test_vec_first(xs):
    assert replace(Vec.create_args(Nat(None), *xs).first()) == xs[0]


@hypothesis.given(list_of_naturals(min_size=1))
def test_vec_rest(xs):
    assert_vector_is_list(Vec.create_args(Nat(None), *xs).rest(), xs[1:])


@hypothesis.given(naturals(), list_of_naturals())
def test_vec_push(x, xs):
    assert_vector_is_list(Vec.create_args(Nat(None), *xs).push(x), [x] + xs)


@hypothesis.given(list_of_naturals(), list_of_naturals())
def test_vec_concat(ls, rs):
    assert_vector_is_list(
        Vec.create_args(Nat(None), *ls).concat(Vec.create_args(Nat(None), *rs)), ls + rs
    )


@hypothesis.given(
    natural_ints().flatmap(
        lambda i: hypothesis.strategies.tuples(
            hypothesis.strategies.just(i), list_of_naturals(min_size=i)
        )
    )
)
def test_vec_drop(i_and_xs):
    i, xs = i_and_xs
    assert_vector_is_list(Vec.create_args(Nat(None), *xs).drop(Nat(i)), xs[i:])


@hypothesis.given(
    natural_ints().flatmap(
        lambda i: hypothesis.strategies.tuples(
            hypothesis.strategies.just(i), list_of_naturals(min_size=i)
        )
    )
)
def test_vec_take(i_and_xs):
    i, xs = i_and_xs
    assert_vector_is_list(Vec.create_args(Nat(None), *xs).take(Nat(i)), xs[:i])


@hypothesis.given(list_of_naturals())
def test_vec_reverse(xs):
    assert_vector_is_list(Vec.create_args(Nat(None), *xs).reverse(), xs[::-1])


@hypothesis.given(hypothesis.strategies.lists(elements=natural_ints(), max_size=5))
def test_vec_reduce(xs):
    v = Vec.create_args(Nat(None), *map(Nat, xs))
    nat_add_abstraction = Abstraction.create_bin(
        lambda x, y: x + y, Nat(None), Nat(None)
    )
    assert replace(v.reduce(Nat(0), nat_add_abstraction)) == Nat(sum(xs))
