import unumpy.multimethods as multimethods
from .multimethods import UFunc, ufunc_list
import torch

from uarray.backend import TypeCheckBackend, register_backend, multimethod

TorchBackend = TypeCheckBackend((torch.Tensor,), convertor=torch.tensor)
register_backend(TorchBackend)


class PyTorchUfunc(TypeCheckBackend):
    def __init__(self):
        super().__init__(TorchBackend.types, TorchBackend._convertor)

    @multimethod(TorchBackend, UFunc.__call__)
    def __call__(self, *args, **kwargs):
        return NotImplemented

    @multimethod(TorchBackend, UFunc.reduce)
    def reduce(self, *args, **kwargs):
        return NotImplemented


_reduce_mapping = {
    'add': torch.sum,
    'multiply': torch.prod,
    'minimum': torch.min,
    'maximum': torch.max,
}


def dummy_reduce(torch_name):
    def reduce(a, axis=0, dtype=None, out=None, keepdims=False):
        if out is not None:
            return NotImplemented

        if axis is None:
            axis = tuple(range(a.dim()))

        return _reduce_mapping[torch_name](a, dim=axis, keepdim=keepdims)

    return reduce


for ufunc_name in ufunc_list:
    if ufunc_name.startswith('arc'):
        torch_name = ufunc_name.replace('arc', 'a')
    else:
        torch_name = ufunc_name

    if hasattr(torch, torch_name):
        temp = PyTorchUfunc()
        TorchBackend.register_instance(getattr(multimethods, ufunc_name),
                                       temp)

        multimethod(temp, UFunc.__call__)(getattr(torch, torch_name))

        if torch_name in _reduce_mapping:
            multimethod(temp, UFunc.reduce)(dummy_reduce(torch_name))

multimethod(TorchBackend, multimethods.arange)(torch.arange)
multimethod(TorchBackend, multimethods.array)(torch.tensor)


@multimethod(TorchBackend, multimethods.asarray)
def asarray(a, dtype=None, order=None):
    if torch.is_tensor(a):
        if a.dtype != dtype:
            return torch.tensor(a, dtype=dtype)
        else:
            ret = a.detach()

        if a.requires_grad:
            ret.requires_grad_()

        return ret

    try:
        import numpy as np

        if isinstance(a, np.ndarray):
            return torch.from_numpy(a)
    except ImportError:
        pass

    return torch.tensor(a, dtype=dtype)


multimethod(TorchBackend, multimethods.zeros)(torch.zeros)
multimethod(TorchBackend, multimethods.ones)(torch.ones)
