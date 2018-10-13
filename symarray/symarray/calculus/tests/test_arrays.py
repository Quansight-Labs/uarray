
from symarray.calculus.integers import Integer
from symarray.calculus.arrays import Array
from symarray.shape import NDShape

def test_basic():
    a = Array('a')
    b = Array('b', shape=NDShape((Integer('n1'), Integer('n2'))))
    n = Integer('n')
    expr = a+n*a+2+b

    print(expr.shape)
    print(expr[1])
