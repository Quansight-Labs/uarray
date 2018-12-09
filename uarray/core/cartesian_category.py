from .category import *


# class PairType(typing.Generic[T_COV, U_COV]):
#     """
#     Covariant because they are immutable
#     """

#     pass


class Pair(matchpy.Operation, typing.Generic[T_COV, U_COV]):
    def __init__(self, l: T_COV, r: U_COV):
        self.l = l
        self.r = r

    def __str__(self):
        return f"({self.l}, {self.r})"


@operation(name="exl")
def Exl(p: PairType[T, U]) -> T:
    ...


@operation(name="exr")
def Exr(p: PairType[T, U]) -> U:
    ...


@replacement
def _exl(l: T, r: U) -> DoubleThunkType[T]:
    return lambda: Exl(Pair(l, r)), lambda: l


@replacement
def _exr(l: T, r: U) -> DoubleThunkType[U]:
    return lambda: Exr(Pair(l, r)), lambda: r


@operation(name="△", infix=True)
def Fork(
    f: FunctionType[T, U], g: FunctionType[T, V]
) -> FunctionType[T, PairType[U, V]]:
    ...


@replacement
def _fork_apply(
    f: FunctionType[T, U], g: FunctionType[T, V], x: T
) -> DoubleThunkType[PairType[U, V]]:
    return lambda: Apply(Fork(f, g), x), lambda: Pair(Apply(f, x), Apply(g, x))


# @operation(name="×", infix=True)
# def Product(
#     f: FunctionType[T, U], g: FunctionType[V, R]
# ) -> FunctionType[PairType[T, V], PairType[U, R]]:
#     ...


# @replacement
# def _product_apply(
#     f: FunctionType[T, U], g: FunctionType[V, R]
# ) -> DoubleThunkType[FunctionType[PairType[T, V], PairType[U, R]]]:
#     exl: Function[PairType[U, V], U] = Function(Exr)
#     exr: Function[PairType[U, V], V] = Function(Exr)

#     return lambda: Product(f, g), lambda: Fork(Compose(f, exl), Compose(g, exr))
