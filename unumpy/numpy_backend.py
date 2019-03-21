import numpy as np
from uarray.backend import TypeCheckBackend, register_backend, instance_multimethod
from .multimethods import UFunc, add

NumpyBackend = TypeCheckBackend((np.ndarray, np.generic, tuple, list), convertor=np.array)
register_backend(NumpyBackend)

NumpyBackend.register_instance(add, np.add)
instance_multimethod(NumpyBackend, UFunc.__call__)(np.ufunc.__call__)
instance_multimethod(NumpyBackend, UFunc.nin.fget)(lambda x: x.nin)
instance_multimethod(NumpyBackend, UFunc.nout.fget)(lambda x: x.nout)
instance_multimethod(NumpyBackend, UFunc.types.fget)(lambda x: x.types)
