import numpy as np
from uarray.backend import (
    Backend,
    register_backend,
    register_implementation,
    DispatchableInstance,
)
from .multimethods import ufunc, ufunc_list, ndarray
import unumpy.multimethods as multimethods
import functools

from typing import Dict

NumpyBackend = Backend()
register_backend(NumpyBackend)

_ufunc_mapping: Dict[ufunc, np.ufunc] = {}


def compat_check(args):
    args = [arg.value if isinstance(arg, DispatchableInstance) else arg for arg in args]
    return all(
        isinstance(arg, (np.ndarray, np.generic)) for arg in args if arg is not None
    )


register_numpy = functools.partial(
    register_implementation, backend=NumpyBackend, compat_check=compat_check
)


def replace_self(func):
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self not in _ufunc_mapping:
            return NotImplemented

        return func(_ufunc_mapping[self], *args, **kwargs)

    return inner


register_numpy(ufunc.__call__)(replace_self(np.ufunc.__call__))
register_numpy(ufunc.reduce)(replace_self(np.ufunc.reduce))
register_numpy(ufunc.accumulate)(replace_self(np.ufunc.accumulate))
register_numpy(ufunc.types.fget)(replace_self(lambda x: x.types))

for ufunc_name in ufunc_list:
    _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(np, ufunc_name)

register_numpy(multimethods.arange)(np.arange)
register_numpy(multimethods.array)(np.array)
register_numpy(multimethods.zeros)(np.zeros)
register_numpy(multimethods.ones)(np.ones)
register_numpy(multimethods.asarray)(np.asarray)

register_numpy(multimethods.broadcast_arrays)(np.broadcast_arrays)
register_numpy(multimethods.broadcast_to)(np.broadcast_to)

register_numpy(multimethods.stack)(np.stack)
register_numpy(multimethods.concatenate)(np.concatenate)

register_numpy(multimethods.argmin)(np.argmin)
register_numpy(multimethods.argmax)(np.argmax)

register_numpy(multimethods.nansum)(np.nansum)
register_numpy(multimethods.nanprod)(np.nanprod)
register_numpy(multimethods.nanmin)(np.nanmin)
register_numpy(multimethods.nanmax)(np.nanmax)

register_numpy(multimethods.std)(np.std)
register_numpy(multimethods.var)(np.var)

register_numpy(multimethods.unique)(np.unique)
register_numpy(multimethods.in1d)(np.in1d)
register_numpy(multimethods.intersect1d)(np.intersect1d)
register_numpy(multimethods.setxor1d)(np.setxor1d)
register_numpy(multimethods.union1d)(np.union1d)

register_numpy(multimethods.sort)(np.sort)
register_numpy(multimethods.lexsort)(np.lexsort)

ndarray.register_convertor(NumpyBackend, np.asarray)
