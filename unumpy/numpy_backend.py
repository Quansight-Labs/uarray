import numpy as np
from uarray.backend import TypeCheckBackend, register_backend, multimethod
from .multimethods import UFunc, ufunc_list
import unumpy.multimethods as multimethods

NumpyBackend = TypeCheckBackend((np.ndarray, np.generic), convertor=np.array,
                                fallback_types=(tuple, list, int, float, bool))
register_backend(NumpyBackend)

multimethod(NumpyBackend, UFunc.__call__)(np.ufunc.__call__)
multimethod(NumpyBackend, UFunc.reduce)(np.ufunc.reduce)
multimethod(NumpyBackend, UFunc.accumulate)(np.ufunc.accumulate)
multimethod(NumpyBackend, UFunc.types.fget)(lambda x: x.types)

for ufunc_name in ufunc_list:
    NumpyBackend.register_instance(getattr(multimethods, ufunc_name),
                                   getattr(np, ufunc_name))

multimethod(NumpyBackend, multimethods.arange)(np.arange)
multimethod(NumpyBackend, multimethods.array)(np.array)
multimethod(NumpyBackend, multimethods.zeros)(np.zeros)
multimethod(NumpyBackend, multimethods.ones)(np.ones)
multimethod(NumpyBackend, multimethods.asarray)(np.asarray)
