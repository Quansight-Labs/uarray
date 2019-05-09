from uarray.backend import Backend, register_backend, register_implementation

try:
    import cupy as cp
    import numpy as np
    import unumpy.multimethods as multimethods
    from .multimethods import ufunc, ufunc_list, ndarray, DispatchableInstance
    from typing import Dict
    import functools

    CupyBackend = Backend()
    register_backend(CupyBackend)

    def compat_check(args):
        return not len(args) or any(
            isinstance(arg.value, cp.ndarray)
            for arg in args
            if isinstance(arg, DispatchableInstance) and arg.value is not None
        )

    register_cupy = functools.partial(
        register_implementation, backend=CupyBackend, compat_check=compat_check
    )

    # experimental support for ufunc from Dask
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

    register_cupy(ufunc.__call__)(replace_self(np.ufunc.__call__))
    register_cupy(ufunc.reduce)(replace_self(np.ufunc.reduce))
    register_cupy(multimethods.arange)(
        lambda start, stop, step, **kwargs: cp.arange(start, stop, step, **kwargs)
    )

    for ufunc_name in ufunc_list:
        if hasattr(np, ufunc_name):
            _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(np, ufunc_name)

    register_cupy(multimethods.array)(cp.array)
    register_cupy(multimethods.asarray)(cp.asarray)

    def _generic(method, args, kwargs, dispatchable_args):
        if not compat_check(dispatchable_args):
            return NotImplemented

        if not hasattr(cp, method.__name__):
            return NotImplemented

        return getattr(cp, method.__name__)(*args, **kwargs)

    CupyBackend.register_implementation(None, _generic)

    ndarray.register_convertor(CupyBackend, cp.asarray)
except ImportError:
    pass
