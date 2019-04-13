from typing import List

import scipy.linalg as spl
from unumpy.numpy_backend import register_numpy

import ulinalg.multimethods as multimethods

__all__: List[str] = []


register_numpy(multimethods.svd)(spl.svd)
