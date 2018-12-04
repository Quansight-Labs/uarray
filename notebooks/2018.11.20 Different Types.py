#%%
from uarray import *
import typing

#%%
shape: CVector[CContent] = Vector(Int(3), Int(2))
content = typing.cast(CIndexFn, unbound("getitem"))
a = NDArray(shape, content)
# print(repr(a))
# print(repr(replace(NDArrayToNestedSequence(a))))
print(Vector(Int(12)))
