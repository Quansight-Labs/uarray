from ..machinery import *
from .naturals import *
from .abstractions import *
from .equality import *

__all__ = [
    "VecType",
    "vec",
    "VecLength",
    "VecContent",
    "VecFirst",
    "VecRest",
    "VecPush",
    "VecConcat",
    "VecDrop",
]

T_cov = typing.TypeVar("T_cov")

# Lists are mappings from integers to values
ListType = AbstractionType[NatType, T_cov]


class VecType(typing.Generic[T_cov]):
    pass


@operation
def Vec(length: NatType, content: ListType[T_cov]) -> VecType[T_cov]:
    """
    Vectors are like lists but with a length associated with them.
    """
    ...


def vec(*xs: T_cov) -> VecType[T_cov]:
    v = Vec(nat(0), never)
    for x in xs[::-1]:
        v = VecPush(x, v)
    return v


@operation
def VecLength(v: VecType[T_cov]) -> NatType:
    ...


@replacement
def _vec_length(length: NatType, content: ListType[T_cov]) -> DoubleThunkType[NatType]:
    return lambda: VecLength(Vec(length, content)), lambda: length


@operation
def VecContent(v: VecType[T_cov]) -> ListType[T_cov]:
    ...


@replacement
def _vec_content(
    length: NatType, content: ListType[T_cov]
) -> DoubleThunkType[ListType[T_cov]]:
    return lambda: VecContent(Vec(length, content)), lambda: content


@operation
def VecFirst(v: VecType[T_cov]) -> T_cov:
    """
    v[0]
    """
    ...


@replacement
def _vec_first(length: NatType, content: ListType[T_cov]) -> DoubleThunkType[T_cov]:
    return lambda: VecFirst(Vec(length, content)), lambda: Apply(content, nat(0))


@operation
def VecRest(v: VecType[T_cov]) -> VecType[T_cov]:
    """
    v[1:]
    """
    ...


@replacement
def _vec_rest(
    length: NatType, content: ListType[T_cov]
) -> DoubleThunkType[VecType[T_cov]]:
    def new_content(idx: NatType) -> T_cov:
        return Apply(content, NatIncr(idx))

    return (
        lambda: VecRest(Vec(length, content)),
        lambda: Vec(NatDecr(length), abstraction(new_content)),
    )


@operation
def VecPush(x: T_cov, v: VecType[T_cov]) -> VecType[T_cov]:
    """
    [x] + v
    """
    ...


@replacement
def _vec_push(
    x: T_cov, length: NatType, content: ListType[T_cov]
) -> DoubleThunkType[VecType[T_cov]]:
    def new_content(idx: NatType) -> T_cov:
        return If(Equal(idx, nat(0)), x, Apply(content, NatDecr(idx)))

    return (
        lambda: VecPush(x, Vec(length, content)),
        lambda: Vec(NatIncr(length), abstraction(new_content)),
    )


"""
Maybe functions should have ranges of values they accept!
Then we don't need this if statement BS

VecAbstraction

([length, fn], [length, fn])...

Do we want functional data structure? Ability to change out this data structure?

Well let's at least keep all API here


Don't expose constructors to other modules
"""


@operation
def VecConcat(l: VecType[T_cov], r: VecType[T_cov]) -> VecType[T_cov]:
    ...


@replacement
def _vec_concat(
    l_length: NatType,
    l_content: ListType[T_cov],
    r_length: NatType,
    r_content: ListType[T_cov],
) -> DoubleThunkType[VecType[T_cov]]:
    def new_content(idx: NatType) -> T_cov:
        return If(
            NatLTE(idx, l_length),
            Apply(l_content, idx),
            Apply(r_content, (NatSubtract(idx, l_length))),
        )

    return (
        lambda: VecConcat(Vec(l_length, l_content), Vec(r_length, r_content)),
        lambda: Vec(NatAdd(l_length, r_length), abstraction(new_content)),
    )


@operation
def VecDrop(n: NatType, v: VecType[T_cov]) -> VecType[T_cov]:
    ...


@replacement
def _vec_drop(
    n: NatType, length: NatType, content: ListType[T_cov]
) -> DoubleThunkType[VecType[T_cov]]:
    def new_content(idx: NatType) -> T_cov:
        return Apply(content, NatAdd(idx, n))

    return (
        lambda: VecDrop(n, Vec(length, content)),
        lambda: Vec(NatSubtract(length, n), abstraction(new_content)),
    )
