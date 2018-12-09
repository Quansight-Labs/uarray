from ..machinery import *


class FunctionType(typing.Generic[T, U]):
    """
    Function from T to U
    """

    pass


@operation(name="apply")
def Apply(f: FunctionType[T, U], x: T) -> U:
    ...


@operation(name="id")
def Identity() -> FunctionType[T, T]:
    ...


@replacement
def _apply_identity(x: T) -> DoubleThunkType[T]:
    id_: FunctionType[T, T] = Identity()
    return lambda: Apply(id_, x), lambda: x


@operation(name="∘", infix=True)
def Compose(g: FunctionType[T, U], f: FunctionType[V, T]) -> FunctionType[V, U]:
    ...


@replacement
def _apply_compose(
    g: FunctionType[T, U], f: FunctionType[V, T], x: V
) -> DoubleThunkType[U]:
    return lambda: Apply(Compose(g, f), x), lambda: Apply(g, Apply(f, x))
