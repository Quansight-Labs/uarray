# pylint: disable=W0614,W0401
from uarray import *


i = Iota(Scalar(10))
x = add(Scalar(1), i)

# two_by_two = Reshape(vector(2, 2), i)
# converted = Index(vector(1, 1), two_by_two)
print(replace(x))


# TODO: Add partial and full index

# TODO: Add
