import numpy as np
from uarray.backend import TypeCheckBackend, register_backend, register_implementation
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


register_implementation(NumpyBackend, ufunc.__call__)(replace_self(np.ufunc.__call__))
register_implementation(NumpyBackend, ufunc.reduce)(replace_self(np.ufunc.reduce))
register_implementation(NumpyBackend, ufunc.accumulate)(replace_self(np.ufunc.accumulate))
register_implementation(NumpyBackend, ufunc.types.fget)(replace_self(lambda x: x.types))

for ufunc_name in ufunc_list:
    _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(np, ufunc_name)

register_implementation(NumpyBackend, multimethods.arange)(np.arange)
register_implementation(NumpyBackend, multimethods.array)(np.array)
register_implementation(NumpyBackend, multimethods.zeros)(np.zeros)
register_implementation(NumpyBackend, multimethods.ones)(np.ones)
register_implementation(NumpyBackend, multimethods.asarray)(np.asarray)
NumpyBackend.register_convertor(ndarray, np.asarray)
