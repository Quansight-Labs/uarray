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
    all_replaced = list(replace_scan(wrapped_expr))
    replaced_expr = all_replaced[-1]
    if not isinstance(replaced_expr, Statement):
        pprint.pprint(all_replaced)
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
        "all_replaced": all_replaced,
        "wrapped_expr": wrapped_expr,
        "ast": ast_,
        "ast_as_source": astunparse.unparse(ast_),
    }
    return wrapped_fn
