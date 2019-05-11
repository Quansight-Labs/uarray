from uarray.backend import register_canonical_backend
from .multimethods import *

import unumpy.numpy_backend as numpy_backend

register_canonical_backend("numpy", numpy_backend)
