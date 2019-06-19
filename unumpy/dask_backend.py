import numpy as np
import dask.array as da
from uarray import Dispatchable
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}

__ua_domain__ = "numpy"


_implementations: Dict = {
    multimethods.ufunc.__call__: np.ufunc.__call__,
    multimethods.arange: lambda start, stop=None, step=None, **kw: da.arange(
        start, stop, step, **kw
    ),
}


def __ua_function__(method, args, kwargs):
    if method in _implementations:
        return _implementations[method](*args, **kwargs)

    if not hasattr(da, method.__name__):
        return NotImplemented

    return getattr(da, method.__name__)(*args, **kwargs)


def __ua_convert__(value, dispatch_type, coerce):
    if dispatch_type is ndarray:
        if not coerce:
            return value
        return da.asarray(value) if value is not None else None

    if dispatch_type is ufunc:
        return getattr(np, value.name)

    return NotImplemented


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner
