import unumpy.multimethods as multimethods
from .multimethods import ufunc, ufunc_list, ndarray
import torch
from typing import Dict, Callable

from uarray.backend import TypeCheckBackend, register_backend, register_implementation

TorchBackend = TypeCheckBackend((torch.Tensor,))
register_backend(TorchBackend)


_reduce_mapping = {
    multimethods.add: torch.sum,  # type: ignore
    multimethods.multiply: torch.prod,  # type: ignore
    multimethods.minimum: torch.min,  # type: ignore
    multimethods.maximum: torch.max,  # type: ignore
}

_ufunc_mapping: Dict[ufunc, Callable] = {}


@register_implementation(TorchBackend, ufunc.__call__)
def __call__(self, *args, out=None):
    if self not in _ufunc_mapping:
        return NotImplemented
    return _ufunc_mapping[self](*args, out=out)


@register_implementation(TorchBackend, ufunc.reduce)
def reduce(self, a, axis=0, dtype=None, out=None, keepdims=False):
    if self not in _reduce_mapping:
        return NotImplemented

    if axis is None:
        axis = tuple(range(a.dim()))

    if isinstance(axis, tuple):
        ret = a
        for dim in tuple(reversed(sorted(axis))):
            ret = _reduce_mapping[self](ret, dim=dim, keepdim=keepdims)

        if out is not None:
            out[...] = ret
            ret = out

    ret = _reduce_mapping[self](a, dim=axis, keepdim=keepdims, out=out)

    if isinstance(ret, tuple):
        ret = ret[0]

    return ret


for ufunc_name in ufunc_list:
    if ufunc_name.startswith('arc'):
        torch_name = ufunc_name.replace('arc', 'a')
    else:
        torch_name = ufunc_name

    if hasattr(torch, torch_name):
        _ufunc_mapping[getattr(multimethods, ufunc_name)] = getattr(torch, torch_name)

register_implementation(TorchBackend, multimethods.arange)(torch.arange)
register_implementation(TorchBackend, multimethods.array)(torch.tensor)


@register_implementation(TorchBackend, multimethods.asarray)
def asarray(a, dtype=None, order=None):
    if torch.is_tensor(a):
        if a.dtype != dtype:
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


register_implementation(TorchBackend, multimethods.zeros)(torch.zeros)
register_implementation(TorchBackend, multimethods.ones)(torch.ones)
TorchBackend.register_convertor(ndarray, asarray)
