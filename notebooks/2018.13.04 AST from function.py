#%%%
import ast
import numpy
import inspect


def create_array(shape):
    return numpy.array(shape)


source = inspect.getsource(create_array)
a = ast.parse(source)
print(ast.dump(a))
