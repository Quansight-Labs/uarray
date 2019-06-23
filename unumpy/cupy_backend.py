try:
    import numpy as np
    import cupy as cp
    from uarray import Dispatchable, wrap_single_convertor
    from .multimethods import ufunc, ufunc_list, ndarray
    import unumpy.multimethods as multimethods
    import functools

    from typing import Dict

    _ufunc_mapping: Dict[ufunc, np.ufunc] = {}

    __ua_domain__ = "numpy"

    _implementations: Dict = {multimethods.ufunc.__call__: cp.ufunc.__call__}

    def __ua_function__(method, args, kwargs):
        if method in _implementations:
            return _implementations[method](*args, **kwargs)

        if not hasattr(cp, method.__name__):
            return NotImplemented

        return getattr(cp, method.__name__)(*args, **kwargs)

    @wrap_single_convertor
    def __ua_convert__(value, dispatch_type, coerce):
        if dispatch_type is ndarray:
            if not coerce:
                return value

            return cp.asarray(value) if value is not None else None

        if dispatch_type is ufunc and hasattr(cp, value.name):
            return getattr(cp, value.name)

        return value

    def replace_self(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            if self not in _ufunc_mapping:
                return NotImplemented

            return func(_ufunc_mapping[self], *args, **kwargs)

        return inner


except ImportError:
    pass
