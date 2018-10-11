
from symarray.integers import Symbol, Number, Terms

def test_basic():
    a = Symbol('a')
    b = Symbol('b')
    print(a+3*b+5+a)
