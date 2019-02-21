import numpy as np

from .lazy_ndarray import to_array
from .arrays import *  # NOQA
from ..core import *
from ..dispatch import *


def test_create_numpy_array():
    a = to_array(Box(np.arange(10).reshape(5, 2)))
    assert replace(a[Array.create_shape(Natural(2), Natural(1))]) == Box(5)
