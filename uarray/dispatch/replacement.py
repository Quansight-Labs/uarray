import typing

from .core import MutableContextType, children, Box

__all__ = ["register"]
T = typing.TypeVar("T")
V = typing.TypeVar("V")
T_call = typing.TypeVar("T_call", bound=typing.Callable)


def register(
    context: MutableContextType, target: T_call
) -> typing.Callable[[T_call], T_call]:
    def inner(fn: T_call, context=context) -> T_call:
        def replacement(op: Box) -> Box:
            args = children(op.value)
            try:
                resulting_box = fn(*args)
            except Exception:
                raise Exception(
                    f"Trying to replace {type(op)} by calling {fn} with {tuple(map(type, args))}: {repr(op)}"
                )
            return resulting_box

        context[target] = replacement
        return fn

    return inner
