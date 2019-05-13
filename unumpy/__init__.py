from uarray.backend import set_global_backend
from .multimethods import *

import unumpy.numpy_backend as numpy_backend

set_global_backend("numpy", numpy_backend)
