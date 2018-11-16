#%%
from uarray.core import *

#%%
s = Scalar(Int(10))

#%%
@operation
def Always(a: T) -> CCallableUnary[T, CContent]:
    ...


#%%
register(Call(Always(w("a")), w("idx")), lambda a, idx: a)


#%%
a_ten = Always(s)


#%%
s = Sequence(Int(10), a_ten)
