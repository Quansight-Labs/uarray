import functools
import typing

from .core_types import *
from .machinery import *


class Int(Symbol[int], NatType):
    pass


@operation
def CallUnary(fn: CallableUnaryType[RET, ARG1], a1: ARG1) -> RET:
    ...


@operation(to_str=lambda fn, a1, a2: f"{fn}({a1}, {a2})")
def CallBinary(fn: CallableBinaryType[RET, ARG1, ARG2], a1: ARG1, a2: ARG2) -> RET:
    ...


@operation
def Array(shape: ShapeType, psi: PsiType[T]) -> ArrayType[T]:
    ...


@operation
def Shape(array: ArrayType[T]) -> ShapeType:
    ...


@replacement
def _shape_of_array(shape: ShapeType, psi: PsiType[T]) -> Pair[ShapeType]:
    return (lambda: Shape(Array(shape, psi)), lambda: shape)


@operation
def Psi(array: ArrayType[T]) -> PsiType[T]:
    ...


@replacement
def _psi_of_array(shape: ShapeType, psi: PsiType[T]) -> Pair[PsiType[T]]:
    return (lambda: Psi(Array(shape, psi)), lambda: psi)


@operation(to_str=lambda val: f"_ -> {val}")
def Always(val: T) -> CallableUnaryType[T, typing.Any]:
    ...


@replacement
def _call_always(val: T, arg: typing.Any) -> Pair[T]:
    return (lambda: CallUnary(Always(val), arg), lambda: arg)


@operation
def Compose(
    l: CallableUnaryType[T, V], r: CallableUnaryType[V, U]
) -> CallableUnaryType[T, U]:
    ...


@replacement
def _call_compose(
    l: CallableUnaryType[T, V], r: CallableUnaryType[V, U], v: U
) -> Pair[T]:
    return (lambda: CallUnary(Compose(l, r), v), lambda: CallUnary(l, CallUnary(r, v)))


# I would think below would work, but it doesn't seem to. So I use protocol way of defining
# callable and this does seem to work
# @symbol
# def PythonUnaryFunction(
#     name: typing.Callable[[ARG1], RET]
# ) -> CallableUnaryType[RET, ARG1]:
#     ...


# class _PythonUnaryFunction(typing_extensions.Protocol[RET, ARG1]):
#     def __call__(
#         self, _name: typing.Callable[[ARG1], RET]
#     ) -> CallableUnaryType[RET, ARG1]:
#         ...


class PythonUnaryFunction(
    Symbol[typing.Callable[[ARG1], RET]], CallableUnaryType[RET, ARG1]
):
    pass
    #     pass
    # class PythonUnaryFunction(matchpy.Symbol, CallableUnaryType[RET, ARG1]):
    #     def __init__(self, name: typing.Callable[[ARG1], RET], variable_name=None):
    #         super().__init__(name, variable_name)

    #     def __str__(self):
    #         return "PythonUnaryFunction"

    # need bogus first arg b/c https://github.com/python/mypy/issues/5485
    # name: typing.Callable[[typing.Any, ARG1], RET]


# class PythonUnaryFunction(
#     typing.Generic[RET, ARG1],
#     Symbol[typing.Callable[[ARG1], RET], CallableUnaryType[RET, ARG1]],
# ):
#     pass


# PythonUnaryFunction: _PythonUnaryFunction = typing.cast(
#     typing.Any, symbol(lambda name: ...)
# )


@replacement
def _call_python_unary_function(
    python_fn: PythonUnaryFunction[ARG1, RET], arg: ARG1
) -> Pair[RET]:
    print(python_fn, arg)
    return (lambda: CallUnary(python_fn, arg), lambda: python_fn.value()(arg))


# @operation(to_str=lambda body, a1: f"({a1} -> {body})")
# def UnaryFunction(body: T, a1: CUnbound) -> CallableUnaryType[T, ARG1]:
#     ...


# @operation(to_str=lambda body, a1, a2: f"({a1}, {a2} -> {body})")
# def BinaryFunction(
#     body: T, a1: CUnbound, a2: CUnbound
# ) -> CallableBinaryType[T, ARG1, ARG2]:
#     ...


# for call_type, fn_type in [(CallBinary, BinaryFunction), (CallUnary, UnaryFunction)]:
#     register(
#         call_type(fn_type(w("body"), ws("args")), ws("arg_vals")),  # type: ignore
#         lambda body, args, arg_vals: matchpy.substitute(
#             body, {arg.variable_name: arg_val for (arg, arg_val) in zip(args, arg_vals)}
#         ),
#     )


# _counter = 0


# def gensym() -> str:
#     global _counter
#     variable_name = f"i{_counter}"
#     _counter += 1
#     return variable_name


# def unbound(variable_name: str = None) -> CUnbound:
#     return Unbound(variable_name=variable_name or gensym())


# def unbound_content(variable_name: str = None) -> CUnboundContent:
#     return typing.cast(CUnboundContent, unbound(variable_name))


# def unary_function(fn: typing.Callable[[ARG1], RET]) -> CallableUnaryType[RET, ARG1]:
#     a1 = unbound()
#     return UnaryFunction(fn(typing.cast(ARG1, a1)), a1)


# def binary_function(
#     fn: typing.Callable[[ARG1, ARG2], RET]
# ) -> CallableBinaryType[RET, ARG1, ARG2]:
#     a1 = unbound()
#     a2 = unbound()
#     return BinaryFunction(fn(typing.cast(ARG1, a1), typing.cast(ARG2, a2)), a1, a2)


@functools.singledispatch
def to_array(v) -> ArrayType:
    """
    Convert some value into a matchpy expression
    """
    raise NotImplementedError()


@to_array.register(matchpy.Expression)
def to_array__expr(v):
    return v


# @to_array.register(tuple)
# def to_array__tuple(t):
#     return vector_of(*(to_array(t_) for t_ in t))


@operation(to_str=lambda items: f"<{' '.join(str(i) for i in items)}>")
def Vector(*items: T) -> VectorType[T]:
    ...


@replacement
def _index_vector(items: typing.Sequence[T], index: Int) -> Pair[T]:
    return (lambda: CallUnary(Vector(*items), index), lambda: items[index.value()])


@operation
def Zero() -> NatType:
    ...


@operation
def VectorFirst(vec: VectorType[T]) -> T:
    ...


@replacement
def _vector_first(vec: VectorType[T]) -> Pair[T]:
    return (lambda: VectorFirst(vec), lambda: CallUnary(vec, Zero()))


@operation
def VectorPush(new_item: T, vec: VectorType[T]) -> VectorType[T]:
    ...


@replacement
def _vector_push(new_item: T, items: typing.Sequence[T]) -> Pair[VectorType[T]]:
    return (
        lambda: VectorPush(new_item, Vector(*items)),
        lambda: Vector(new_item, *items),
    )


@operation
def VectorConcat(l: VectorType[T], r: VectorType[T]) -> VectorType[T]:
    ...


@replacement
def _vector_concat(
    l_items: typing.Sequence[T], r_items: typing.Sequence[T]
) -> Pair[VectorType[T]]:
    return (
        lambda: VectorConcat(Vector(*l_items), Vector(*r_items)),
        lambda: Vector(*l_items, *r_items),
    )


@operation
def VectorToArray(length: NatType, vec: VectorType[T]) -> ArrayType[T]:
    ...


# vector_first_boxed: typing.Callable[[VectorType[T]], T] = Box(VectorFirst)

first_index: CallableUnaryType[
    NatType, CallableUnaryType[NatType, NatType]
] = PythonUnaryFunction(VectorFirst)


@replacement
def _vector_to_array(length: NatType, vec: VectorType[T]) -> Pair[ArrayType[T]]:

    return (
        lambda: VectorToArray(length, vec),
        lambda: Array(Vector(length), Compose(vec, first_index)),
    )


# scalar_fn: CallableUnaryType[ArrayType, CContent] = typing.cast(
#     CUnaryPythonFunction[ArrayType, CContent], UnaryPythonFunction(Scalar)
# )


@operation
def Unify(*args: T) -> T:
    ...


# TODO: Support unification on unequal but equivelent form
# similar to question of equivalencies of lambda calculus, i.e. lambda a: a + 1 == lambda b: b + 1
# even though variables are different name
# Also need to be able to say some thing *could* be equal at runtime, whereas some others cannot be.
# i.e. If two `Value`s are unequal, they cannot be unified. However, if two arbitrary expressions are not equal
# at compile time, they still could end up being equal at runtime.
@replacement
def _unify_single(x: T) -> Pair[T]:
    return lambda: Unify(x), lambda: x


@replacement
def _unify_multiple(x: T, xs: typing.Sequence[T]) -> Pair[T]:
    return lambda: Unify(x, x, *xs), lambda: Unify(x, *xs)
