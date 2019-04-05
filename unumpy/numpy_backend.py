import numpy as np
from uarray.backend import TypeCheckBackend, register_backend, multimethod
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

NumpyBackend = TypeCheckBackend((np.ndarray, np.generic), fallback_types=(tuple, list, int, float, bool))
register_backend(NumpyBackend)

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner


multimethod(NumpyBackend, ufunc.__call__)(replace_self(np.ufunc.__call__))
multimethod(NumpyBackend, ufunc.reduce)(replace_self(np.ufunc.reduce))
multimethod(NumpyBackend, ufunc.accumulate)(replace_self(np.ufunc.accumulate))
multimethod(NumpyBackend, ufunc.types.fget)(replace_self(lambda x: x.types))

for ufunc_name in ufunc_list:
    _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(np, ufunc_name)

multimethod(NumpyBackend, multimethods.arange)(np.arange)
multimethod(NumpyBackend, multimethods.array)(np.array)
multimethod(NumpyBackend, multimethods.zeros)(np.zeros)
multimethod(NumpyBackend, multimethods.ones)(np.ones)
multimethod(NumpyBackend, multimethods.asarray)(np.asarray)
NumpyBackend.register_convertor(ndarray, np.asarray)
