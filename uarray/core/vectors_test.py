import hypothesis
import typing
from ..machinery import replace
from .vectors import *
from .naturals import *
from .pairs import *
from .naturals_test import naturals, natural_ints
from .abstractions import *

T = typing.TypeVar("T")


@hypothesis.strategies.defines_strategy
def list_of_naturals(min_size=0, max_size=5):
    return hypothesis.strategies.lists(
        elements=naturals(), min_size=min_size, max_size=max_size
    )


def assert_vector_is_list(v: VecType[T], xs: typing.Sequence[T]):
    v = replace(v)
    assert replace(Exl(v)) == nat(len(xs))
    l = Exr(v)
    for i, x in enumerate(xs):
        assert replace(Apply(l, nat(i))) == x


@hypothesis.given(list_of_naturals())
def test_constructor_has_length_and_can_get(xs):
    assert_vector_is_list(vec(*xs), xs)


@hypothesis.given(list_of_naturals(min_size=1))
def test_vec_first(xs):
    assert replace(VecFirst(vec(*xs))) == xs[0]


@hypothesis.given(list_of_naturals(min_size=1))
def test_vec_rest(xs):
    assert_vector_is_list(VecRest(vec(*xs)), xs[1:])


@hypothesis.given(naturals(), list_of_naturals())
def test_vec_push(x, xs):
    assert_vector_is_list(VecPush(x, vec(*xs)), [x] + xs)


@hypothesis.given(list_of_naturals(), list_of_naturals())
def test_vec_concat(ls, rs):
    assert_vector_is_list(VecConcat(vec(*ls), vec(*rs)), ls + rs)


@hypothesis.given(
    natural_ints().flatmap(
        lambda i: hypothesis.strategies.tuples(
            hypothesis.strategies.just(i), list_of_naturals(min_size=i)
        )
    )
)
def test_vec_drop(i_and_xs):
    i, xs = i_and_xs
    assert_vector_is_list(VecDrop(nat(i), vec(*xs)), xs[i:])


@hypothesis.given(
    natural_ints().flatmap(
        lambda i: hypothesis.strategies.tuples(
            hypothesis.strategies.just(i), list_of_naturals(min_size=i)
        )
    )
)
def test_vec_take(i_and_xs):
    i, xs = i_and_xs
    assert_vector_is_list(VecTake(nat(i), vec(*xs)), xs[:i])


@hypothesis.given(list_of_naturals())
def test_vec_reverse(xs):
    assert_vector_is_list(VecReverse(vec(*xs)), xs[::-1])


@abstraction
def nat_add_abstraction(p: PairType[NatType, NatType]):
    return NatAdd(Exl(p), Exr(p))


@hypothesis.given(hypothesis.strategies.lists(elements=natural_ints(), max_size=5))
def test_vec_reduce(xs):
    assert replace(VecReduce(nat_add_abstraction, nat(0), vec(*map(nat, xs)))) == nat(
        sum(xs)
    )
