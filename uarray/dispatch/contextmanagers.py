import typing
import contextlib

from .core import *

__all__ = ["setcontext", "localcontext"]


@contextlib.contextmanager
def setcontext(context: ContextType) -> typing.Iterator[ContextType]:
    token = global_context.set(context)
    yield context
    global_context.reset(token)


@contextlib.contextmanager
def localcontext() -> typing.Iterator[ContextType]:
    """
    with localcontext() as ctx:
        ctx["some_name"] = lambda node: ...

        node.replace()
    """
    new_context = MapChainCallable()
    token = global_context.set(ChainCallableMap(new_context, global_context.get()))
    yield new_context
    global_context.reset(token)
