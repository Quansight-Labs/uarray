import numpy as np

from .lazy_ndarray import to_array
from ..core import *
from ..dispatch import *


def test_create_numpy_array():
    a = to_array(Box(np.arange(10).reshape(5, 2)))
    assert replace(a[Array.create_shape(Nat(2), Nat(1))]).value == 5
