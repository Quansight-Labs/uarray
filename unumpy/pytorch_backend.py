import torch

from uarray.backend import TypeCheckBackend, register_backend

TorchBackend = TypeCheckBackend((torch.Tensor,), convertor=torch.Tensor)
register_backend(TorchBackend)
