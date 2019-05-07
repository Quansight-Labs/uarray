import dask.array as da
import dask
import numpy as np
import unumpy.multimethods as multimethods
from .multimethods import ufunc, ufunc_list, ndarray, DispatchableInstance
from typing import Dict
import functools
import uarray as ua

from uarray.backend import Backend, register_backend, register_implementation

DaskBackend = Backend()
register_backend(DaskBackend)


def compat_check(args):
    return any(isinstance(arg.value, dask.array.core.Array) for arg in args
               if isinstance(arg, DispatchableInstance) and arg.value is not None)


register_dask = functools.partial(register_implementation, backend=DaskBackend, compat_check=compat_check)

# experimental support for ufunc from Dask
_ufunc_mapping: Dict[ufunc, da.gufunc] = {}

def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner


register_dask(ufunc.__call__)(replace_self(da.gufunc.__call__))
register_dask(ufunc.reduce)(replace_self(np.ufunc.reduce))


for ufunc_name in ufunc_list:
    if hasattr(np, ufunc_name):
        _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(np, ufunc_name)

register_dask(multimethods.array)(dask.array.core.Array)
register_dask(multimethods.asarray)(da.asarray)


def _generic(method, args, kwargs, dispatchable_args):
    if not compat_check(dispatchable_args):
        return NotImplemented

    if hasattr(da, method.__name__):
        getattr(da, method.__name__)(*args, **kwargs)

    return NotImplemented


DaskBackend.register_implementation(None, _generic)


