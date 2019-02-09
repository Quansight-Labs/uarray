import ast
import functools
import inspect
import typing

import astunparse
import numpy

from .core import *
from .dispatch import *
from .numpy import *

# indices will have length now for arrays
__all__ = ["jit"]
T_call = typing.TypeVar("T_call", bound=typing.Callable)


def jit(*dims: int) -> typing.Callable[[T_call], T_call]:
    def inner(fn: T_call) -> T_call:
        arg_names = list(inspect.signature(fn).parameters.keys())
        nargs = len(arg_names)

        def wrapper_fn(*args):
            return fn(
                *(
                    LazyNDArray.create(to_array(arg)).with_dim(Nat(dim))
                    for (arg, dim) in zip(args, dims)
                )
            ).array

        orig_res = Abstraction.create_nary(
            wrapper_fn, arg_names, *([Array(None, Box(None))] * nargs)
        )
        res = replace(orig_res)
        # return res
        new_res = res
        for arg_name in arg_names:
            new_res = new_res(Box(AST(ast.Name(arg_name, ast.Load()))))

        # return new_res
        new_res = replace(new_res)
        # return new_res
        replaced = replace(to_ast(new_res))
        # return replaced
        res_ast = replaced.value
        if not isinstance(res_ast, AST):
            raise NotImplementedError("Couldn't compile to AST")
        args_ = ast.arguments(
            args=[ast.arg(arg=a, annotation=None) for a in arg_names],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        )
        fn = ast.Module(
            body=[
                ast.FunctionDef(
                    name="fn",
                    args=args_,
                    body=[*res_ast.init, ast.Return(value=res_ast.get)],
                    decorator_list=[],
                    returns=None,
                )
            ]
        )
        source = astunparse.unparse(fn)
        locals_ = {}
        exec(
            compile(ast.fix_missing_locations(fn), filename="<ast>", mode="exec"),
            {"numpy": numpy},
            locals_,
        )
        wrapped_fn = functools.wraps(fn)(locals_["fn"])
        wrapped_fn.source = source
        wrapped_fn.res = res
        wrapped_fn.orig_res = orig_res
        return wrapped_fn

    return inner
