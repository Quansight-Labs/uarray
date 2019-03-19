try:
    import torch

    from uarray.backend import TypeCheckBackend, register_backend

    TorchBackend = TypeCheckBackend((torch.Tensor, tuple, list), convertor=torch.Tensor.new_tensor)
    register_backend(TorchBackend)
except ImportError:
    pass
