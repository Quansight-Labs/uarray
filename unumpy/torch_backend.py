import unumpy.multimethods as multimethods
from .multimethods import ufunc, ufunc_list, ndarray
import torch
from uarray import Dispatchable

__ua_domain__ = "numpy"


def compat_check(args):
    args = [arg.value if isinstance(arg, Dispatchable) else arg for arg in args]
    return all(
        isinstance(arg, torch.Tensor) or callable(arg)
        for arg in args
        if arg is not None
    )


def asarray(a, dtype=None, order=None):
    if torch.is_tensor(a):
        if dtype is None or a.dtype != dtype:
            ret = torch.tensor(a, dtype=dtype)
            if a.requires_grad:
                ret.requires_grad_()
            return ret

        return a
    try:
        import numpy as np

        if isinstance(a, np.ndarray):
            return torch.from_numpy(a)
    except ImportError:
        pass

    return torch.tensor(a, dtype=dtype)


_implementations = {
    multimethods.ufunc.__call__: lambda x, *a, **kw: x(*a, **kw),
    multimethods.asarray: asarray,
    multimethods.array: torch.Tensor,
    multimethods.arange: lambda start, stop, step, **kwargs: torch.arange(
        start, stop, step, **kwargs
    ),
}


def __ua_function__(method, args, kwargs, dispatchable_args):
    if not compat_check(dispatchable_args):
        return NotImplemented

    if method in _implementations:
        return _implementations[method](*args, **kwargs)

    if not hasattr(torch, method.__name__):
        return NotImplemented

    return getattr(torch, method.__name__)(*args, **kwargs)


def __ua_convert__(value, dispatch_type, coerce):
    if dispatch_type is ndarray:
        if not coerce:
            return value

        return asarray(value) if value is not None else None

    if dispatch_type is ufunc and value in _ufunc_mapping:
        return _ufunc_mapping[value]

    return NotImplemented


_ufunc_mapping = {}


for ufunc_name in ufunc_list:
    if ufunc_name.startswith("arc"):
        torch_name = ufunc_name.replace("arc", "a")
    else:
        torch_name = ufunc_name

    if hasattr(torch, torch_name):
        _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(torch, torch_name)
