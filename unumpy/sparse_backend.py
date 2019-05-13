import numpy as np
import sparse
from uarray.backend import DispatchableInstance
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}

__ua_domain__ = "numpy"


def compat_check(args):
    args = [arg.value if isinstance(arg, DispatchableInstance) else arg for arg in args]
    return all(
        isinstance(arg, (sparse.SparseArray, np.generic, np.ufunc))
        for arg in args
        if arg is not None
    )


_implementations: Dict = {
    multimethods.ufunc.__call__: np.ufunc.__call__,
    multimethods.ufunc.reduce: np.ufunc.reduce,
}


def __ua_function__(method, args, kwargs, dispatchable_args):
    if not compat_check(dispatchable_args):
        return NotImplemented

    if method in _implementations:
        return _implementations[method](*args, **kwargs)

    if not hasattr(sparse, method.__name__):
        return NotImplemented

    return getattr(sparse, method.__name__)(*args, **kwargs)


def __ua_coerce__(value, dispatch_type):
    if dispatch_type is ndarray:
        if value is None:
            return None

        if isinstance(value, sparse.SparseArray):
            return value

        return sparse.as_coo(np.asarray(value))

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
