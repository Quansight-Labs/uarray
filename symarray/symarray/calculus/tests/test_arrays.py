
from symarray.calculus.integers import Integer
from symarray.calculus.arrays import Array
from symarray.shape import NDShape

def test_basic():
    from symarray.arrays import A, B
    from symarray.ints import n, m
    from symarray.scalars import a, b
    A = Array('A')
    B = Array('B', shape=NDShape((Integer('n1'), Integer('n2'))))
    expr = A+n*A+2+B
    #assert str(expr)==''
    print(expr[1])


def test_index():
    from symarray.arrays import A, B
    from symarray.ints import n1,n2, s1,s2
    from symarray.scalars import a, b
    assert str(A[n1,n2]) == 'A[n1, n2]'
    assert str(A[1,n2]) == 'A[1, n2]'
    assert str(A[n1]) == 'A[n1]'
    assert str(A[0]) == 'A[0]'
    assert str((A+B)[n1]) == 'A[n1] + B[n1]'
    assert str((A+b*B-B)[n1]) == 'A[n1] + (-1 + b) * B[n1]'
    assert str(A[n1][n2]) == 'A[n1, n2]'

    assert str(A[s1:n2]) == 'A[s1:n2]'
    assert str(A[s1:n2, ::3]) == 'A[s1:n2, ::3]'
    
def test_power():
    from symarray.arrays import A, B
    from symarray.ints import n, m

    assert A**1 == A
    assert A**2 == A*A
    assert str(A**3) == 'A ** 3'
    assert str(A**n) == 'A ** n'
    assert str((A+B)**n) == '(A + B) ** n'
    assert str(A**0) == '<<1>>'
