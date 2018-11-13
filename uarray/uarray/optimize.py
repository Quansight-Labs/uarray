import ast
import inspect

import astunparse
import numpy as np

from .ast import *
from .lazy_ndarray import LazyNDArray
from .numpy import logger


def optimize(*shapes: typing.Sequence[int]):
    def inner(initial_fn):
        arg_names = list(inspect.signature(initial_fn).parameters.keys())
        logger.debug("arg_names: %s", arg_names)
        args_ids = list(map(Identifier, arg_names))
        logger.debug("args_ids: %s", args_ids)

        args = [LazyNDArray(np_array_from_id(id_)) for id_ in args_ids]
        logger.debug("args: %s", args)
        args_with_shape = [arg.has_shape(shape) for arg, shape in zip(args, shapes)]
        logger.debug("args_with_shape: %s", args_with_shape)
        resulting_expr = LazyNDArray(initial_fn(*args_with_shape)).expr
        logger.debug("resulting_expr: %s", resulting_expr)
        wrapped_expr = DefineFunction(
            ToNPArray(resulting_expr, ShouldAllocate(True)), *args_ids
        )
        logger.debug("wrapped_expr: %s", wrapped_expr)
        all_replaced = list(replace_scan(wrapped_expr))
        logger.debug("all_replaced: %s", all_replaced)
        replaced_expr = all_replaced[-1]
        logger.debug("replaced_expr: %s", replaced_expr)
        if not isinstance(replaced_expr, Statement):
            raise RuntimeError(
                f"Could not replace {repr(replaced_expr)} into AST statement"
            )
        ast_ = replaced_expr.name
        logger.debug("ast_: %s", ast_)
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

    return inner
