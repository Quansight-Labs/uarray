import ast
import inspect
import pprint

import astunparse
import numpy as np

from .ast import *
from .lazy_ndarray import LazyNDArray


def optimize(initial_fn):
    arg_names = list(inspect.signature(initial_fn).parameters.keys())
    args_ids = list(map(Identifier, arg_names))
    args = list(map(LazyNDArray, map(np_array_from_id, args_ids)))
    resulting_expr = to_array(LazyNDArray(initial_fn(*args)))
    wrapped_expr = DefineFunction(
        ToNPArray(resulting_expr, ShouldAllocate(True)), *args_ids
    )
    replaced_expr = replace(wrapped_expr)
    if not isinstance(replaced_expr, Statement):
        pprint.pprint(replaced_expr)
        raise RuntimeError(
            f"Could not replace {repr(replaced_expr)} into AST statement"
        )
    ast_ = replaced_expr.name
    locals_ = {}
    exec(
        compile(ast.fix_missing_locations(ast_), filename="<ast>", mode="exec"),
        {"np": np},
        locals_,
    )
    wrapped_fn = functools.wraps(initial_fn)(locals_["fn"])
    wrapped_fn.__optimize_steps__ = {
        "args": args,
        "resulting_expr": resulting_expr,
        "wrapped_expr": wrapped_expr,
        "ast": ast_,
        "ast_as_source": astunparse.unparse(ast_),
    }
    return wrapped_fn
