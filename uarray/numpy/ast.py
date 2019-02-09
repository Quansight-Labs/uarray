"""
Support reading and compiling to python AST of NumPy API

Array -> AST of numpy.ndarray
Vector -> tuple
Natural -> number
"""
import ast
import dataclasses
import typing

import numpy

from .lazy_ndarray import to_array, numpy_ufunc
from ..core import *
from ..dispatch import *

__all__ = ["AST", "to_ast"]
T_box = typing.TypeVar("T_box", bound=Box)
ctx = MapChainCallable()
default_context.append(ctx)


@dataclasses.dataclass(frozen=True)
class AST:
    # AST expression that returns this value
    get: ast.AST
    # AST statements that initialize this value
    init: typing.Iterable[ast.AST] = ()

    def include(self, other: "AST") -> "AST":
        return AST(self.get, (*other.init, *self.init))

    def includes(self, *others: "AST") -> "AST":
        for other in others:
            self = self.include(other)
        return self


def is_ast(b: Box[object]) -> bool:
    return isinstance(b.value, AST)


@register(ctx, to_array)
def to_array(b: Box) -> Array:
    if not is_ast(b):
        return NotImplemented
    return Array(b.value, Box(None))


def to_ast(b: T_box) -> T_box:
    return b.replace(Operation(to_ast, (b,)))


def _ast_abstraction_inner(
    fn: typing.Callable[..., AST], rettype: T_box, *args: Box[AST]
) -> T_box:
    asts: typing.List[AST] = [a.value for a in args]
    return rettype.replace(fn(*asts))


def create_ast_abstraction(
    fn: typing.Callable[..., AST], rettype: Box, n_args: int
) -> T_box:
    return Abstraction.create_nary_native(
        Partial(_ast_abstraction_inner, (fn, rettype)), rettype, *[is_ast] * n_args
    )


def as_ast(fn: typing.Callable[..., AST], rettype: T_box, *args: Box) -> T_box:
    """
    Takes in a function mapping arguments of type AST to an AST 
    """
    res: typing.Any = create_ast_abstraction(fn, rettype, len(args))
    for a in args:
        res = res(to_ast(a))
    return typing.cast(T_box, res)


@register(ctx, to_ast)
def to_ast_numbers(b: T_box) -> T_box:
    if not isinstance(b.value, (int, float)):
        return NotImplemented
    return b.replace(AST(ast.Num(b.value)))


@register(ctx, to_ast)
def to_ast_tuple(b: T_box) -> T_box:
    if not isinstance(b, Vec) or not isinstance(b.value, VecData):
        return NotImplemented

    length, lst = b.value.length, b.value.list
    if not isinstance(length.value, int):
        return NotImplemented

    def inner(*args: AST) -> AST:
        return AST(ast.Tuple([a.get for a in args], ast.Load())).includes(*args)

    return as_ast(inner, b, *(lst[Nat(i)] for i in range(length.value)))


# @register(ctx, Vec)
# def _convert_list(length: Nat, lst: List[T_box]) -> Vec[T_box]:
#     """
#     When we know length, convert abstraction list to exact list
#     """
#     if not isinstance(length.value, int) or not concrete(lst):
#         return NotImplemented
#     return Vec.create(
#         length, List.create(lst.dtype, *(lst[Nat(i)] for i in range(length.value)))
#     )


@register(ctx, to_ast)
def to_ast__ufunc(b: T_box) -> T_box:
    if not isinstance(b.value, Operation) or b.value.name != numpy_ufunc:
        return NotImplemented
    ufunc, *args = b.value.args
    if not isinstance(ufunc.value, numpy.ufunc):
        return NotImplemented

    def _call_ufunc(*args: AST, name: str = ufunc.value.__name__) -> AST:
        return AST(
            ast.Call(
                ast.Attribute(
                    value=ast.Name(
                        id="numpy",
                        ctx=ast.Load(),  # TODO: Maybe don't get off global numpy?
                    ),
                    attr=name,
                    ctx=ast.Load(),
                ),
                args=[a.get for a in args],
                keywords=[],
            )
        ).includes(*args)

    return as_ast(_call_ufunc, b, *args)


_i = 0


def _gen_id() -> str:
    global _i
    i = f"v{_i}"
    _i += 1
    return i


def create_id() -> typing.Tuple[ast.AST, ast.AST]:
    """
    return store/load expressions for new name
    """
    i = _gen_id()
    return ast.Name(i, ast.Store()), ast.Name(i, ast.Load())


def create_for(
    store_index: ast.AST,
    store_result: ast.AST,
    load_result: ast.AST,
    n_ast: AST,
    initial_ast: AST,
    load_loop_result: AST,
) -> AST:
    return AST(
        load_result,
        [
            ast.Assign([store_result], initial_ast.get),
            ast.For(
                store_index,
                ast.Call(ast.Name("range", ast.Load()), [n_ast.get], []),
                [
                    *load_loop_result.init,
                    ast.Assign([store_result], load_loop_result.get),
                ],
                [],
            ),
        ],
    ).includes(initial_ast, n_ast)


@register(ctx, to_ast)
def to_ast_loop(b: T_box) -> T_box:
    if not isinstance(b.value, Operation) or b.value.name != Nat.loop:
        return NotImplemented
    n, initial, fn = typing.cast(
        typing.Tuple[Nat, T_box, Abstraction[T_box, Abstraction["Nat", T_box]]],
        b.value.args,
    )

    store_index, load_index = create_id()
    store_result, load_result = create_id()

    return as_ast(
        Partial(create_for, (store_index, store_result, load_result)),
        b,
        n,
        initial,
        fn(initial.replace(AST(load_result)))(Nat(AST(load_index))),
    )


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not is_ast(self):
        return NotImplemented
    ndim = Nat(
        AST(ast.Attribute(self.value.get, "ndim", ast.Load())).include(self.value)
    )

    @List.from_function
    def list_fn(idx: Nat, self_ast=self.value) -> Nat:
        def inner(idx_ast: AST, self_ast=self_ast) -> AST:
            return AST(
                ast.Subscript(
                    ast.Attribute(self_ast.get, "shape", ast.Load()),
                    ast.Index(idx_ast.get),
                    ast.Load(),
                )
            ).includes(self_ast, idx_ast)

        return as_ast(inner, Nat(None), idx)

    return Vec.create(ndim, list_fn)


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[Vec[Nat], T_box]:
    if not is_ast(self):
        return NotImplemented

    @Array.create_idx_abs
    def idx_abs(idx: Vec[Nat], self_ast=self.value) -> T_box:
        def inner(idx_ast: AST, self_ast=self_ast) -> AST:
            if not idx_ast.get.elts:  # type: ignore
                return self_ast
            return AST(
                ast.Subscript(self_ast.get, ast.Index(idx_ast.get), ast.Load())
            ).includes(self_ast, idx_ast)

        return as_ast(inner, self.dtype, idx)

    return idx_abs


@register(ctx, to_ast)
def to_ast__array(b: T_box) -> T_box:
    if not isinstance(b, Array):
        return NotImplemented

    idx_store, idx_load = create_id()
    array_store, array_load = create_id()

    def array_fn(length: AST, val: AST) -> AST:
        return AST(
            array_load,
            [
                ast.Assign(
                    [array_store],
                    ast.Call(
                        ast.Attribute(
                            ast.Name("numpy", ast.Load()), "empty", ast.Load()
                        ),
                        [length.get],
                        [ast.keyword(arg="dtype", value=ast.Str("int64"))],
                    ),
                ),
                ast.For(
                    idx_store,
                    ast.Call(ast.Name("range", ast.Load()), [length.get], []),
                    [
                        *val.init,
                        ast.Assign(
                            [
                                ast.Subscript(
                                    array_load, ast.Index(idx_load), ast.Store()
                                )
                            ],
                            val.get,
                        ),
                    ],
                    [],
                ),
            ],
        ).includes(length)

    # for now assume 1d array. In future, add ravel.
    vec = b.to_vec()
    return as_ast(array_fn, b, vec.length, vec.list[Nat(AST(idx_load))])


@register(ctx, to_ast)
def to_ast_already_ast(b: T_box) -> T_box:
    if not is_ast(b):
        return NotImplemented
    return b
