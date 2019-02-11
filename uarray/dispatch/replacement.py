import typing

from .core import *

__all__ = ["register", "ReturnNotImplemented"]
T = typing.TypeVar("T")
V = typing.TypeVar("V")
T_call = typing.TypeVar("T_call", bound=typing.Callable)


class ReturnNotImplemented(Exception):
    pass


def register(
    context: MutableContextType, target: T_call, default=False
) -> typing.Callable[[T_call], T_call]:
    def inner(fn: T_call, context=context, target=target, default=default) -> T_call:
        def replacement(op: Box, fn=fn, context=context, default=default) -> Box:
            args = children(op.value)
            if default and not all(concrete(a.value) for a in args):
                return NotImplemented
            try:
                resulting_box = fn(*args)
            except ReturnNotImplemented:
                return NotImplemented
            except Exception:
                raise Exception(
                    f"Trying to replace {type(op)} by calling {fn} with {tuple(map(type, args))}: {repr(op)}"
                )
            return resulting_box

        context[target] = replacement
        return fn

    return inner
