#%%
from ast import parse
from astunparse import dump

#%%
print(dump(parse("1 + 1").body[0]))

#%%
import inspect

#%%
f = lambda: 1 + 1
print(inspect.getsource(f))
