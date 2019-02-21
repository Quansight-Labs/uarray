import contextlib
import typing

from .core import ContextType, global_context

__all__ = ["setcontext"]


@contextlib.contextmanager
def setcontext(context: ContextType) -> typing.Iterator[ContextType]:
    token = global_context.set(context)
    yield context
    global_context.reset(token)
