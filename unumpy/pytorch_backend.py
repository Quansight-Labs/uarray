import unumpy.multimethods as multimethods
from .multimethods import UFunc, ufunc_list
import torch

from uarray.backend import TypeCheckBackend, register_backend, instance_multimethod

TorchBackend = TypeCheckBackend((torch.Tensor, tuple, list), convertor=torch.Tensor.new_tensor)
register_backend(TorchBackend)


class PyTorchUfunc:
    def __init__(self, func):
        self.func = func

    @instance_multimethod(TorchBackend, UFunc.__call__)
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


for ufunc_name in ufunc_list:
    if hasattr(torch, ufunc_name):
        temp = PyTorchUfunc(getattr(torch, ufunc_name))
        TorchBackend.register_instance(getattr(multimethods, ufunc_name),
                                       temp)
