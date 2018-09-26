# pylint: disable=W0614,W0401
from uarray import *


i = Iota(Scalar(10))
two_by_two = Reshape(vector(2, 2), i)
print(replace_debug(as_vector(Take(vector(1), two_by_two))))
