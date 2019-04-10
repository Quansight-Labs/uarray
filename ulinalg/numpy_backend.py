from typing import List

import scipy.linalg as spl
from unumpy.numpy_backend import NumpyBackend

import ulinalg.multimethods as multimethods
from uarray import register_implementation

__all__: List[str] = []


register_implementation(NumpyBackend, multimethods.svd)(spl.svd)
