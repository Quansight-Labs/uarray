from typing import List

import scipy.linalg as spl
from unumpy.numpy_backend import NumpyBackend

from .methods import svd

__all__: List[str] = []


def svd_impl(method, args, kwargs):
    return spl.svd(*args, **kwargs)


NumpyBackend.register_method(svd, svd_impl)
