from typing import List

try:
    import torch
    from unumpy.torch_backend import register_torch
    import ulinalg.multimethods as multimethods

    __all__: List[str] = []

    def svd_impl(a, full_matrices=True, compute_uv=True, overwrite_a=False, check_finite=True, lapack_driver='gesdd'):
        u, s, v = torch.svd(a, some=full_matrices, compute_uv=compute_uv)

        if compute_uv:
            return u, s, v
        else:
            return s

    register_torch(multimethods.svd)(svd_impl)

except ImportError:
    pass
