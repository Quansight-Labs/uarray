import ast
import inspect

import IPython.display
import astunparse
import numpy as np

from .ast import *
from .lazy_ndarray import LazyNDArray
from .logging import logger


def optimize(initial_fn_or_shape, *shapes: typing.Sequence[int]):
    if callable(initial_fn_or_shape):
        initial_fn = initial_fn_or_shape
        new_shapes = None
    else:
        new_shapes = [initial_fn_or_shape, *shapes]
        initial_fn = None

    def inner(initial_fn):
        arg_names = list(inspect.signature(initial_fn).parameters.keys())
        logger.debug("arg_names: %s", arg_names)
        args_ids = list(map(Identifier, arg_names))
        logger.debug("args_ids: %s", args_ids)

        args = [LazyNDArray(np_array_from_id(id_)) for id_ in args_ids]
        for a in args:
            logger.debug("arg: %s", a)
        if new_shapes:
            args_with_shape = [
                arg.has_shape(shape) for arg, shape in zip(args, new_shapes)
            ]
        else:
            args_with_shape = args
        for a_with_s in args_with_shape:
            logger.debug("arg_with_shape: %s", a_with_s)

        resulting_expr = LazyNDArray(initial_fn(*args_with_shape)).expr
        logger.debug("resulting_expr: %s", resulting_expr)
        wrapped_expr = DefineFunction(
            ToNPArray(resulting_expr, ShouldAllocate(True)), *args_ids
        )
        logger.debug("wrapped_expr: %s", wrapped_expr)
        all_replaced = list(replace_scan(wrapped_expr))
        for i, v in enumerate(all_replaced):
            logger.debug(f"{i} %s", v)
        replaced_expr = all_replaced[-1]
        if (
            not isinstance(replaced_expr, VectorCallable)
            or not replaced_expr.operands
            or not isinstance(replaced_expr.operands[0], Statement)
        ):
            raise RuntimeError(
                f"Could not replace {repr(replaced_expr)} into AST statement"
            )
        ast_ = replaced_expr[0].name
        source = astunparse.unparse(ast_)
        logger.debug("source: %s", IPython.display.Code(source))
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
            "ast_as_source": source,
        }
        return wrapped_fn

    if not shapes:
        return inner(initial_fn)
    return inner
