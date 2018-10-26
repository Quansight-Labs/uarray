from uarray import *
from uarray.ast import *
import numpy as np


# logging.basicConfig(level=logging.DEBUG)


@optimize()
def some_fn(a, b):
    return np.multiply.outer(a, b)[10]


first = ToSequenceWithDim(np_array_from_id(Identifier("a")), Value(1))
second = ToSequenceWithDim(np_array_from_id(Identifier("b")), Value(1))
e = some_fn(first, second)
final = replace(
    DefineFunction(ToNPArray(e, ShouldAllocate(True)), Identifier("a"), Identifier("b"))
)


print(final)
