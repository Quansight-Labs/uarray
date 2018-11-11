#%%
from uarray.core import *

#%%
s = Scalar(Int(10))


class Always(matchpy.Operation):
    name = "Always"
    arity = matchpy.Arity(1, False)


#%%
@operation
def Always(a: T) -> CCallableUnary[T, CContent]:
    ...


#%%
always_ten = Always(s)
repr(Always(Int(10)))

#%%
s = Sequence(Int(5), Always(Scalar(Int(10))))


#%%
def hi(x):
    return lambda: x


h = hi
print(hi(10)())
print(hi(20)())
