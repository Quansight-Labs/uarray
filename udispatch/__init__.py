"""
Lazy multiple dispatching.
"""

from .contextmanagers import *  # NOQA
from .core import *  # NOQA
from .replacement import *  # NOQA
from .operations import *  # NOQA

__version__ = '0.5.0'

__all__ = [
    "Operation",
    "Box",
    "copy",
    "concrete",
    "concrete_operation",
    "ReturnNotImplemented",
    "extract_args",
    "operation_with_default",
    "extract_value",
    "Operation",
    "operation",
    "map_children",
    "global_context",
    "ReplacementType",
    "MapChainCallable",
    "ContextType",
    "KeyType",
    "children",
    "replace_inplace_generator",
    "key",
    "ChildrenType",
    "replace",
    "ChainCallable",
    "setcontext",
    "register",
]
