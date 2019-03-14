import numpy as np
from uarray.backend import TypeCheckBackend, register_backend

NumpyBackend = TypeCheckBackend((np.ndarray, np.generic, tuple, list), convertor=np.array)
register_backend(NumpyBackend)
