import xnd
import gumath.functions as fn
import gumath as gu
import unumpy.multimethods as multimethods
from .multimethods import UFunc, ufunc_list

from uarray.backend import TypeCheckBackend, register_backend, multimethod

XndBackend = TypeCheckBackend((xnd.xnd,), convertor=xnd.array)
register_backend(XndBackend)


@multimethod(XndBackend, UFunc.reduce)
def reduce_(self, a, axis=0, dtype=None, out=None, keepdims=False):
    if out is not None or not isinstance(self, gu.gufunc):
        return NotImplemented
    return gu.reduce(self, a, axes=axis, dtype=dtype)


multimethod(XndBackend, UFunc.__call__)(gu.gufunc.__call__)

for ufunc_name in ufunc_list:
    if hasattr(fn, ufunc_name):
        XndBackend.register_instance(getattr(multimethods, ufunc_name),
                                     getattr(fn, ufunc_name))

multimethod(XndBackend, multimethods.array)(xnd.array)
multimethod(XndBackend, multimethods.asarray)(xnd.array.from_buffer)
