import typing
import ast
import dataclasses
from ..core import *
from ..dispatch import *
from .lazy_ndarray import to_array, numpy_ufunc
import numpy

__all__ = ["AST", "ast_replace_ctx"]
T_box = typing.TypeVar("T_box", bound=Box)
ctx = MapChainCallable()
default_context.append(ctx)

ast_replace_ctx = MapChainCallable()

# Automatic casting would be helpful here...
# Look at that book for casting rules
# Graph of all types -> casting between them?


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


@register_type(ast_replace_ctx, int)
def _int(v: int) -> AST:
    return AST(ast.Num(v))


@register_type(ast_replace_ctx, float)
def _float(v: float) -> AST:
    return AST(ast.Num(v))


@register(ast_replace_ctx, List)
def _list(*args: T_box) -> List[Box]:
    if not all(is_ast(a) for a in args):
        return NotImplemented
    args_ast: typing.Tuple[AST, ...] = tuple(a.value for a in args)
    # dtype of returned list doesn't matter, only value will be used in replacement
    return List(
        AST(ast.Tuple(elts=[a.get for a in args_ast], ctx=ast.Load())).includes(
            *args_ast
        ),
        Box(None),
    )


@register(ast_replace_ctx, Vec)
def _vec(length: Nat, lst: List[Box]) -> Vec[Box]:
    if not is_ast(lst):
        return NotImplemented
    return Vec(lst.value, lst.dtype)


@register(ast_replace_ctx, numpy_ufunc)
def _ufunc(ufunc: Box[numpy.ufunc], *args: Box) -> Box:
    if not all(map(is_ast, args)):
        return NotImplemented
    args_ast: typing.List[AST] = [a.value for a in args]
    return Box(
        AST(
            ast.Call(
                ast.Attribute(
                    value=ast.Name(
                        id="numpy",  # TODO: Maybe don't get off global numpy?
                        ctx=ast.Load(),
                    ),
                    attr=ufunc.value.__name__,
                    ctx=ast.Load(),
                ),
                args=[a.get for a in args_ast],
                keywords=[],
            )
        ).includes(*args_ast)
    )


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


@register(ast_replace_ctx, Nat.loop)
def _loop(
    self: Nat, initial: T_box, fn: Abstraction[T_box, Abstraction["Nat", T_box]]
) -> T_box:
    if not is_ast(self) or not is_ast(initial):
        return NotImplemented
    idx_store, idx_load = create_id()
    res_store, res_load = create_id()

    def create_for(res: AST, initial_ast=initial.value, self_ast=self.value) -> AST:
        return AST(
            res_load,
            [
                ast.Assign([res_store], initial_ast.get),
                ast.For(
                    idx_store,
                    ast.Call(ast.Name("range", ast.Load()), [self_ast.get], []),
                    [ast.Assign([res_store], res.get)],
                    [],
                ),
            ],
        ).includes(initial_ast, self_ast)

    return create_ast_abs(create_for, fn.rettype.rettype)(
        fn(initial._replace(AST(res_load)))(Nat(AST(idx_load)))
    )


def create_ast_abs(
    fn: typing.Callable[[AST], AST], rettype: T_box
) -> Abstraction[Box, T_box]:
    def inner(b_ast: Box) -> T_box:
        if not is_ast(b_ast):
            return NotImplemented
        b_val = b_ast.value
        return rettype._replace(fn(b_val).include(b_val))

    inner.__name__ = f"wrapped:{fn.__name__}"
    return Abstraction.create_native(inner, rettype)


def create_tuple_list_ast(a: AST, dtype: T_box) -> List[T_box]:
    def inner(i: AST, a=a) -> AST:
        return AST(ast.Subscript(a.get, ast.Index(i.get), ast.Load())).include(a)

    return List.from_abs(create_ast_abs(inner, dtype))


@register(ctx, Array._get_shape)
def _get_shape(self: Array[T_box]) -> Vec[Nat]:
    if not is_ast(self):
        return NotImplemented
    ndim = AST(ast.Attribute(self.value.get, "ndim", ast.Load()))
    shape = AST(ast.Attribute(self.value.get, "shape", ast.Load()))
    return Vec.create(length=Nat(ndim), lst=create_tuple_list_ast(shape, Nat(None)))


@register(ctx, Array._get_idx_abs)
def _get_idx_abs(self: Array[T_box]) -> Abstraction[List[Nat], T_box]:
    if not is_ast(self):
        return NotImplemented

    def idx_abs(idx: AST, self_val=self.value) -> AST:
        if not idx.get.elts:
            return self_val
        return AST(ast.Subscript(self_val.get, ast.Index(idx.get), ast.Load())).include(
            self_val
        )

    return create_ast_abs(idx_abs, self.dtype)
