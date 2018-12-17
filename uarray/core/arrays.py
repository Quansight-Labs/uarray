from ..machinery import *
from .naturals import *
from .vectors import *
from .abstractions import *

__all__ = [
    "ShapeType",
    "IdxType",
    "ArrayType",
    "array_0d",
    "array_1d",
    "ArrayShape",
    "ArrayIdx",
    "VecToArray",
    "ArrayToVec",
]
T_cov = typing.TypeVar("T_cov")


"""
Should arrays depend on vector implementation? Should the destructture them?

Yes -> less replacement, cleaner code
    requires replacement happen on Vec instead of some other vec like thing
No -> Creates abstraction layer between them. Independence
    allows replacement on non vec thing
    maybe we dont want this... i.e. like Array, so if we have a non Vec VecType thing
    we can define custom replacements for it....

    But this is *within* array replacements. so what is use case??

Underlying question -> Should abstract definitions only be applied on abstract inputs or all inputs?

    -> Only abstract
        Difference between "type" of thing and instantiation of that thing with default constructor

        Operations apply on Type but replacements are defined with default constructor.

        Like Nats within vectors. Vector doesn't know about `Int` implementation.

        So ->>??

Another way of framing: How do we make most explicit what backends need to define?
i.e. if you define a custom XXX what needs to be implemented on it? 
"""

ShapeType = VecType[NatType]
IdxType = AbstractionType[ShapeType, T_cov]


class ArrayType(typing.Generic[T_cov]):
    pass


@operation
def Array(shape: ShapeType, idx: IdxType[T_cov]) -> ArrayType[T_cov]:
    ...


def array_0d(x: T_cov) -> ArrayType[T_cov]:
    """
    Returns a scalar array of `x`.
    """
    return Array(vec(), const(x))


def array_1d(*xs: T_cov) -> ArrayType[T_cov]:
    """
    Returns a vector array of `xs`.
    """
    return VecToArray(vec(*xs))


@operation
def ArrayShape(a: ArrayType[T_cov]) -> ShapeType:
    ...


@replacement
def _array_shape(shape: ShapeType, idx: IdxType[T_cov]) -> DoubleThunkType[ShapeType]:
    return lambda: ArrayShape(Array(shape, idx)), lambda: shape


@operation
def ArrayIdx(a: ArrayType[T_cov]) -> IdxType[T_cov]:
    ...


@replacement
def _array_idx(
    shape: ShapeType, idx: IdxType[T_cov]
) -> DoubleThunkType[IdxType[T_cov]]:
    return (lambda: ArrayIdx(Array(shape, idx)), lambda: idx)


@operation
def VecToArray(v: VecType[T_cov]) -> ArrayType[T_cov]:
    """
    Returns a 1D array that has contents of the vector.
    """
    ...


@replacement
def _vec_to_array(v: VecType[T_cov]) -> DoubleThunkType[ArrayType[T_cov]]:
    def fn():
        shape = vec(VecLength(v))

        def idx(idx: ShapeType) -> T_cov:
            return Apply(VecContent(v), VecFirst(idx))

        return Array(vec(VecLength(v)), abstraction(idx))

    return (lambda: VecToArray(v), fn)


@operation
def ArrayToVec(a: ArrayType[T_cov]) -> VecType[T_cov]:
    """
    Returns a vector from a 1D array
    """
    ...


"""
Should I keep writing tests or go on to array definitions?

Array definitions? need to get these working. Can write tests for them, then go back and add lower level tests if they fail.
"""


@replacement
def _array_to_vec(
    shape: ShapeType, idx: IdxType[T_cov]
) -> DoubleThunkType[VecType[T_cov]]:
    # TODO: Maybe move to vectors file b/c it is vector constructor?
    from .vectors import Vec

    def fn() -> VecType[T_cov]:
        length = VecFirst(shape)

        def content(vec_idx: NatType) -> T_cov:
            return Apply(idx, vec(vec_idx))

        return Vec(length, abstraction(content))

    return (lambda: ArrayToVec(Array(shape, idx)), fn)
