from .vectors import *

VecNatType = VecType[NatType]
IndexType = FunctionType[VecNatType, T]
# (shape, index)
ArrayType = PairType[VecNatType, IndexType[T]]

# @operation
# def VecToArray(v: VecType[T]) -> ArrayType[T]:
#     """
#     Returns a 1D array that has contents of the vector.
#     """
#     ...


def array_0d(x: T) -> ArrayType[T]:
    """
    Returns a scalar array of `x`.
    """
    return Pair(vec(), Const(x))


def array_1d(*xs: T) -> ArrayType[T]:
    """
    Returns a vector array of `xs`.
    """
    return VecToArray(vec(*xs))


@operation
def VecToArray(v: VecType[T]) -> ArrayType[T]:
    """
    Returns a 1D array that has contents of the vector.
    """
    ...


@replacement
def _vec_to_array(v: VecType[T]) -> DoubleThunkType[ArrayType[T]]:
    vec_first: Function[VecType[NatType], NatType] = Function(VecFirst)
    return (
        lambda: VecToArray(v),
        lambda: Pair(vec(Exl(v)), Compose(Exr(v), vec_first)),
    )


@operation
def ArrayToVec(a: ArrayType[T]) -> VecType[T]:
    """
    Returns a 1D array that has contents of the vector.
    """
    ...


@replacement
def _array_to_vec(a: ArrayType[T]) -> DoubleThunkType[VecType[T]]:
    def _replacement() -> VecType[T]:
        shape = Exr(Exl(a))
        length = Apply(shape, Int(0))
        idx = Exr(a)

        def list_index(i):
            Apply(idx, Pair(Int(0), List(i)))

        vec_first: FunctionType[VecType[T], T] = Function(VecFirst)
        reveal_type(vec_first)
        reveal_type(idx)
        lst = Compose(vec_first, idx)
        return Pair(length, lst)

    return (lambda: ArrayToVec(a), _replacement)


# @replacement
# def _array_to_vector(
#     shape_list: ListType[NatType], array_index: ArrayIndexType[T]
# ) -> ThunkPairType[VectorType[T]]:

#     return (
#         lambda: ArrayToVector(Array(Vector(Int(1), shape_list), array_index)),
#         lambda: Vector(
#             ApplyUnary(shape_list, Int(0)), Compose(array_index, singleton_list)
#         ),
#     )
