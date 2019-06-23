import numpy as np
import xnd
import gumath.functions as fn
import gumath as gu
import uarray as ua
from uarray import Dispatchable, wrap_single_convertor
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}

__ua_domain__ = "numpy"


_implementations: Dict = {
    multimethods.ufunc.__call__: gu.gufunc.__call__,
    multimethods.ufunc.reduce: gu.reduce,
}


def __ua_function__(method, args, kwargs):
    if method in _implementations:
        return _implementations[method](*args, **kwargs)

    return _generic(method, args, kwargs)


@wrap_single_convertor
def __ua_convert__(value, dispatch_type, coerce):
    if dispatch_type is ndarray:
        return convert(value, coerce=coerce) if value is not None else None

    if dispatch_type is ufunc and hasattr(fn, value.name):
        return getattr(fn, value.name)

    return NotImplemented


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner


def _generic(method, args, kwargs):
    try:
        import numpy as np
        import unumpy.numpy_backend as NumpyBackend
    except ImportError:
        return NotImplemented

    with ua.set_backend(NumpyBackend, coerce=True):
        try:
            out = method(*args, **kwargs)
        except TypeError:
            return NotImplemented

    return convert_out(out, coerce=False)


def convert_out(x, coerce):
    if isinstance(x, (tuple, list)):
        return type(x)(map(lambda x: convert_out(x, coerce=coerce), x))

    return convert(x, coerce=coerce)


def convert(x, coerce):
    if isinstance(x, np.ndarray):
        return xnd.array.from_buffer(x)
    elif isinstance(x, np.generic):
        try:
            return xnd.array.from_buffer(memoryview(x))
        except TypeError:
            return NotImplemented
    else:
        if not coerce:
            return value
        return xnd.array(x)
