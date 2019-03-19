from typing import List

import scipy.linalg as spl
from unumpy.numpy_backend import NumpyBackend

import ulinalg.multimethods as multimethods
from uarray import multimethod

__all__: List[str] = []


multimethod(NumpyBackend, multimethods.svd)(spl.svd)
