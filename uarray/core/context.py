from ..dispatch import *

__all__ = ["ctx"]

ctx = MapChainCallable()

default_context.append(ctx)
