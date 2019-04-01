from xnd import xnd
import gumath.functions as fn
import unumpy.multimethods as multimethods
from .multimethods import UFunc, ufunc_list

from uarray.backend import TypeCheckBackend, register_backend, multimethod

XndBackend = TypeCheckBackend((xnd,), convertor=xnd)
register_backend(XndBackend)

gufunc = type(fn.add)

multimethod(XndBackend, UFunc.__call__)(gufunc.__call__)

for ufunc_name in ufunc_list:
    if hasattr(fn, ufunc_name):
        XndBackend.register_instance(getattr(multimethods, ufunc_name),
                                     getattr(fn, ufunc_name))
