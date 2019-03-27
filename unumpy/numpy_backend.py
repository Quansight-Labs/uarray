import numpy as np
from uarray.backend import TypeCheckBackend, register_backend, instance_multimethod
from .multimethods import UFunc, ufunc_list
import unumpy.multimethods as multimethods

NumpyBackend = TypeCheckBackend((np.ndarray, np.generic, tuple, list), convertor=np.array)
register_backend(NumpyBackend)

instance_multimethod(NumpyBackend, UFunc.__call__)(np.ufunc.__call__)
instance_multimethod(NumpyBackend, UFunc.reduce)(np.ufunc.reduce)
instance_multimethod(NumpyBackend, UFunc.accumulate)(np.ufunc.accumulate)
instance_multimethod(NumpyBackend, UFunc.nin.fget)(lambda x: x.nin)
instance_multimethod(NumpyBackend, UFunc.nout.fget)(lambda x: x.nout)
instance_multimethod(NumpyBackend, UFunc.types.fget)(lambda x: x.types)

for ufunc_name in ufunc_list:
    NumpyBackend.register_instance(getattr(multimethods, ufunc_name),
                                   getattr(np, ufunc_name))
