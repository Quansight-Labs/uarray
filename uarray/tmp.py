# pylint: disable=W0614,W0401
from uarray import *


i = Iota(Scalar(10))
print(replace_debug(as_vector(Reshape(vector(2, 2), i)), False))
