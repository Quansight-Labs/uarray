import xnd
import gumath.functions as fn
import gumath as gu
import unumpy.multimethods as multimethods
from .multimethods import ufunc, ufunc_list, ndarray
from typing import Dict
import functools

from uarray.backend import TypeCheckBackend, register_backend, register_implementation

XndBackend = TypeCheckBackend((xnd.xnd,))
register_backend(XndBackend)

_ufunc_mapping: Dict[ufunc, gu.gufunc] = {}


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner


@register_implementation(XndBackend, ufunc.reduce)
@replace_self
def reduce_(self, a, axis=0, dtype=None, out=None, keepdims=False):
    if out is not None:
        return NotImplemented
    return gu.reduce(self, a, axes=axis, dtype=dtype)


register_implementation(XndBackend, ufunc.__call__)(replace_self(gu.gufunc.__call__))

for ufunc_name in ufunc_list:
    if hasattr(fn, ufunc_name):
        _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(fn, ufunc_name)

register_implementation(XndBackend, multimethods.array)(xnd.array)
register_implementation(XndBackend, multimethods.asarray)(xnd.array)

XndBackend.register_convertor(ndarray, xnd.array)
