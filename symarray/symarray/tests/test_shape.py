
from symarray.shape import NDShape
from symarray.calculus import Integer, Int

def test_basic_gamma():
    n, m, i, j, o, s = map(Integer, 'nmijos')
    
    shape = NDShape((n,m), offset = o, itemsize = s)
    assert str(shape) == 'NDShape(dims=(n, m), strides=(n, 1), offset=o, itemsize=s)'
    assert str(shape(i, j)) == 'i * n * s + j * s + o'
    assert str(shape(3, 5)) == '3 * n * s + o + 5 * s'

    shape = NDShape((n,m), offset = 0, itemsize = 1)
    assert str(shape) == 'NDShape(dims=(n, m), strides=(n, 1), offset=0, itemsize=1)'
    assert str(shape(i, j)) == 'i * n + j'
    assert str(shape(3, 5)) == '5 + 3 * n'
    
    shape = NDShape((n,10), offset = o, itemsize = s)
    assert str(shape) == 'NDShape(dims=(n, 10), strides=(n, 1), offset=o, itemsize=s)'
    assert str(shape(i, j)) == 'i * n * s + j * s + o'
    assert str(shape(3, 5)) == '3 * n * s + o + 5 * s'
    
    shape = NDShape((10,m), offset = o, itemsize = s)
    assert str(shape) == 'NDShape(dims=(10, m), strides=(10, 1), offset=o, itemsize=s)'
    assert str(shape(i, j)) == '10 * i * s + j * s + o'
    assert str(shape(3, 5)) == 'o + 35 * s'
