import xnd
import gumath.functions as fn
import gumath as gu
import unumpy.multimethods as multimethods
from .multimethods import ufunc, ufunc_list, ndarray, DispatchableInstance
from typing import Dict
import functools

from uarray.backend import Backend, register_backend, register_implementation

XndBackend = Backend()
register_backend(XndBackend)


def compat_check(args):
    args = [arg.value if isinstance(arg, DispatchableInstance) else arg for arg in args]
    return all(isinstance(arg, xnd.xnd) for arg in args if arg is not None)


register_xnd = functools.partial(register_implementation, backend=XndBackend, compat_check=compat_check)

_ufunc_mapping: Dict[ufunc, gu.gufunc] = {}


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner


@register_xnd(ufunc.reduce)
@replace_self
def reduce_(self, a, axis=0, dtype=None, out=None, keepdims=False):
    if out is not None:
        return NotImplemented
    return gu.reduce(self, a, axes=axis, dtype=dtype)


register_xnd(ufunc.__call__)(replace_self(gu.gufunc.__call__))

for ufunc_name in ufunc_list:
    if hasattr(fn, ufunc_name):
        _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(fn, ufunc_name)

register_xnd(multimethods.array)(xnd.array)
register_xnd(multimethods.asarray)(xnd.array)


def asarray(a):
    if isinstance(a, xnd.xnd):
        return a

    if hasattr(a, '__buffer__'):
        return xnd.array.from_buffer(a)

    return xnd.array(a)


ndarray.register_convertor(XndBackend, asarray)
