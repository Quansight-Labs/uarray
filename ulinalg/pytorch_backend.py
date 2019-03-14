from typing import List

import torch
from unumpy.pytorch_backend import TorchBackend

from .methods import svd

__all__: List[str] = []


def svd_torch(self, args, kwargs):
    def svd_impl(a, full_matrices=True, compute_uv=True, overwrite_a=False, check_finite=True, lapack_driver='gesdd'):
        u, s, v = torch.svd(a, some=full_matrices, compute_uv=compute_uv)

        if compute_uv:
            return u, s, v
        else:
            return s

    return svd_impl(*args, **kwargs)


TorchBackend.register_method(svd, svd_torch)
