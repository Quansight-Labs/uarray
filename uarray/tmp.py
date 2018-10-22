# pylint: disable=W0614,W0401
from uarray import *
import numpy as np
import logging

# logging.basicConfig(level=logging.DEBUG)


def cross_product_index(a, b):
    return np.multiply.outer(a, b)


args = (np.arange(10), np.arange(100))

assert np.array_equal(cross_product_index(*args), optimize(cross_product_index)(*args))
