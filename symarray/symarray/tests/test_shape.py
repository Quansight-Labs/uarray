
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

def test_subarray_shape():
    n, m, i, j, o, s, k, l = map(Integer, 'nmijoskl')
    shape = NDShape((n,m), offset = o, itemsize = s)
    assert str(shape[i, j]) == 'NDShape(dims=(), strides=(), offset=i * n * s + j * s + o, itemsize=s)' # item is 0-dim array
    assert str(shape[i, j]()) == 'i * n * s + j * s + o' # pointer to item value

    assert str(shape[i]) == 'NDShape(dims=(m), strides=(1), offset=i * n * s + o, itemsize=s)' # i-th row

    assert str(shape[i:j]) == 'NDShape(dims=(-i + j, m), strides=(n, 1), offset=i * n * s + o, itemsize=s)'
    assert str(shape[i:j, k:l]) == 'NDShape(dims=(-i + j, -k + l), strides=(n, 1), offset=i * n * s + k * s + o, itemsize=s)'
    assert str(shape[i:j][:,k:l]) == str(shape[i:j, k:l])

    assert str(shape[i:j:k]) == 'NDShape(dims=(floor(-i + j, k), m), strides=(k * n, 1), offset=i * n * s + o, itemsize=s)'
