"""Universal array library"""
from .dispatch import *  # NOQA
from .core import *  # NOQA
from .moa import *  # NOQA
from .nested_sequence import *  # NOQA
from .numpy import *  # NOQA
from .optimize import *  # NOQA
from .visualize import *  # NOQA

# Cannot use this because
# https://github.com/python/mypy/issues/4949
# __all__ = (
#     dispatch.__all__
#     + core.__all__
#     + moa.__all__
#     + nested_sequence.__all__
#     + numpy.__all__
#     + optimize.__all__
#     + visualize.__all__
# )

__all__ = [
    "Operation",
    "Box",
    "copy",
    "concrete",
    "ReturnNotImplemented",
    "operation_with_default",
    "extract_args",
    "extract_value",
    "map_children",
    "global_context",
    "ReplacementType",
    "ContextType",
    "MutableContextType",
    "KeyType",
    "children",
    "replace_inplace_generator",
    "key",
    "ChildrenType",
    "replace",
    "ChainCallable",
    "MapChainCallable",
    "ChainCallableMap",
    "default_context",
    "setcontext",
    "localcontext",
    "includecontext",
    "register",
    "Abstraction",
    "Variable",
    "rename_variables",
    "Partial",
    "Array",
    "Bool",
    "List",
    "Natural",
    "Vec",
    "MoA",
    "concrete_operation",
    "create_python_array",
    "to_python_array",
    "create_python_bin_abs",
    "AST",
    "to_ast",
    "LazyNDArray",
    "to_box",
    "to_array",
    "numpy_ufunc",
    "jit",
    "visualize_diff",
    "visualize_progress",
    "display_ops",
]

__version__ = "0.4"
