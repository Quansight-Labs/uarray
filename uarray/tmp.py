# pylint: disable=W0614,W0401
from uarray import *


i = Iota(Scalar(10))
x = add(Scalar(1), i)

# two_by_two = Reshape(vector(2, 2), i)
# converted = Index(vector(1, 1), two_by_two)
print(replace(x))


register(
    InnerProduct(op1, op2, x, x2),
    lambda
)

register(
    InnerProduct(op1, op2, x, BinOpScalar(scalar, op3, x2)),
    lambda
)