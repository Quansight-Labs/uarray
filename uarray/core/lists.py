from .naturals import *

ListType = FunctionType[NatType, T_COV]

# recursive types aren't supported yet so we don't define lists recursively
# https://github.com/python/mypy/issues/731
@operation(to_str=lambda items: f"<{' '.join(str(i) for i in items)}>")
def List(*items: T) -> ListType[T]:
    """
    Creates an indexing function based on the items.
    """
    ...


@replacement
def _list_apply(items: typing.Sequence[T], index: Int) -> DoubleThunkType[T]:
    return (lambda: Apply(List(*items), index), lambda: items[index.value()])


@operation
def ListLength(l: ListType[T]) -> NatType:
    ...


@replacement
def _list_length(*xs: T) -> DoubleThunkType[NatType]:
    return lambda: ListLength(List(*xs)), lambda: Int(len(xs))


@operation
def ListFirst(l: ListType[T]) -> T:
    ...


@replacement
def _list_first(x: T, xs: typing.Sequence[T]) -> DoubleThunkType[T]:
    return (lambda: ListFirst(List(x, *xs)), lambda: x)


@operation
def ListRest(v: ListType[T]) -> ListType[T]:
    ...


@replacement
def _list_rest(x: T, xs: typing.Sequence[T]) -> DoubleThunkType[ListType[T]]:
    return (lambda: ListRest(List(x, *xs)), lambda: List(*xs))


@operation
def ListPush(x: T, v: ListType[T]) -> ListType[T]:
    ...


@replacement
def _list_push(x: T, xs: typing.Sequence[T]) -> DoubleThunkType[ListType[T]]:
    return (lambda: ListPush(x, List(*xs)), lambda: List(x, *xs))


@operation
def ListConcat(l: ListType[T], r: ListType[T]) -> ListType[T]:
    ...


@replacement
def _list_concat(
    l_xs: typing.Sequence[T], r_xs: typing.Sequence[T]
) -> DoubleThunkType[ListType[T]]:
    return (lambda: ListConcat(List(*l_xs), List(*r_xs)), lambda: List(*l_xs, *r_xs))


@operation
def ListDrop(n: NatType, vec: ListType[T]) -> ListType[T]:
    ...


@replacement
def _list_drop(n: Int, xs: typing.Sequence[T]) -> DoubleThunkType[ListType[T]]:
    return (lambda: ListDrop(n, List(*xs)), lambda: List(*xs[n.value() :]))
