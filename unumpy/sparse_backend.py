import numpy as np
import sparse
from uarray.backend import Dispatchable
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}

__ua_domain__ = "numpy"


_implementations: Dict = {
    multimethods.ufunc.__call__: np.ufunc.__call__,
    multimethods.ufunc.reduce: np.ufunc.reduce,
}


def __ua_function__(method, kwargs):
    if method in _implementations:
        return _implementations[method](**kwargs)

    if not hasattr(sparse, method.__name__):
        return NotImplemented

    return getattr(sparse, method.__name__)(**kwargs)


def __ua_convert__(value, dispatch_type, coerce):
    if dispatch_type is ndarray:
        if not coerce:
            return value

        if value is None:
            return None

        if isinstance(value, sparse.SparseArray):
            return value

        return sparse.as_coo(np.asarray(value))

    if dispatch_type is ufunc:
        return getattr(np, value.name)

    return value


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner
