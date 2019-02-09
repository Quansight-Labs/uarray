import contextlib
import typing

from .core import ContextType, global_context, MapChainCallable, ChainCallableMap

__all__ = ["setcontext", "localcontext", "includecontext"]


@contextlib.contextmanager
def setcontext(context: ContextType) -> typing.Iterator[ContextType]:
    token = global_context.set(context)
    yield context
    global_context.reset(token)


@contextlib.contextmanager
def includecontext(context: ContextType) -> typing.Iterator[ContextType]:
    new_context = ChainCallableMap(global_context.get(), context)
    token = global_context.set(new_context)
    yield new_context
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
