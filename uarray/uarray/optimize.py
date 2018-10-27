import ast
import astunparse
import numpy as np
import inspect
from .ast import *
from .lazy_ndarray import LazyNDArray
import pprint


def optimize(initial_fn):
    arg_names = list(inspect.signature(initial_fn).parameters.keys())
    args_ids = list(map(Identifier, arg_names))
    args = list(map(LazyNDArray, map(np_array_from_id, args_ids)))
    resulting_expr = to_expression(LazyNDArray(initial_fn(*args)))
    wrapped_expr = DefineFunction(
        ToNPArray(resulting_expr, ShouldAllocate(True)), *args_ids
    )
    replaced_expr = replace(wrapped_expr)
    if not isinstance(replaced_expr, Statement):
        raise RuntimeError(
            f"Could not replace {repr(replaced_expr)} into AST statement"
        )
    ast_ = replaced_expr.name
    l = {}
    exec(
        compile(ast.fix_missing_locations(ast_), filename="<ast>", mode="exec"),
        {"np": np},
        l,
    )
    wrapped_fn = functools.wraps(initial_fn)(l["fn"])
    wrapped_fn.__optimize_steps__ = {
        "args": args,
        "resulting_expr": resulting_expr,
        "wrapped_expr": wrapped_expr,
        "ast": ast_,
        "ast_as_source": astunparse.unparse(ast_),
    }
    return wrapped_fn
