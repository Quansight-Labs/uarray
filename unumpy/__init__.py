from .multimethods import *

try:
    from .numpy_backend import NumpyBackend
except ImportError:
    pass