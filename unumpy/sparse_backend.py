import sparse
import numpy as np
import unumpy.multimethods as multimethods
from .multimethods import ufunc, ufunc_list, ndarray, DispatchableInstance
from typing import Dict
import functools

from uarray.backend import Backend, register_backend, register_implementation

SparseBackend = Backend()
register_backend(SparseBackend)


def compat_check(args):
    return not len(args) or \
        all(isinstance(arg.value, sparse.SparseArray) for arg in args
            if isinstance(arg, DispatchableInstance) and arg.value is not None)


register_sparse = functools.partial(register_implementation, backend=SparseBackend, compat_check=compat_check)

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        try:
            return func(_ufunc_mapping[self], *args, **kwargs)
        except TypeError:
            return NotImplemented

    return inner


register_sparse(ufunc.__call__)(replace_self(np.ufunc.__call__))
register_sparse(ufunc.reduce)(replace_self(np.ufunc.reduce))


for ufunc_name in ufunc_list:
    if hasattr(np, ufunc_name):
        _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(np, ufunc_name)

register_sparse(multimethods.array)(sparse.COO)
register_sparse(multimethods.asarray)(sparse.as_coo)


def _generic(method, args, kwargs, dispatchable_args):
    if not compat_check(dispatchable_args):
        return NotImplemented

    if hasattr(sparse, method.__name__):
        return getattr(sparse, method.__name__)(*args, **kwargs)

    return NotImplemented


SparseBackend.register_implementation(None, _generic)


def convert(val):
    if isinstance(val, sparse.SparseArray):
        return val

    if isinstance(val, np.ndarray):
        return sparse.as_coo(val)

    return sparse.as_coo(np.asarray(val))


ndarray.register_convertor(SparseBackend, convert)
