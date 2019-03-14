import numpy as np
from uarray.backend import TypeCheckBackend, register_backend

NumpyBackend = TypeCheckBackend((np.ndarray, tuple, list), convertor=np.array)
register_backend(NumpyBackend)
