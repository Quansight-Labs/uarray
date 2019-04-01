import unumpy.multimethods as multimethods
from .multimethods import UFunc, ufunc_list
import torch

from uarray.backend import TypeCheckBackend, register_backend, multimethod

TorchBackend = TypeCheckBackend((torch.Tensor,), convertor=torch.tensor)
register_backend(TorchBackend)


class PyTorchUfunc:
    def __init__(self, func):
        self.func = func

    @multimethod(TorchBackend, UFunc.__call__)
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


for ufunc_name in ufunc_list:
    if ufunc_name.startswith('arc'):
        torch_name = ufunc_name.replace('arc', 'a')
    else:
        torch_name = ufunc_name

    if hasattr(torch, torch_name):
        temp = PyTorchUfunc(getattr(torch, torch_name))
        TorchBackend.register_instance(getattr(multimethods, ufunc_name),
                                       temp)

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
