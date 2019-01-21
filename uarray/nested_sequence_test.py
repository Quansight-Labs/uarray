from .dispatch import *
from .nested_sequence import *


def test_isomoprhic():
    shape = (2, 2)
    values = (1, 2), (3, 4)
    python_array = create_python_array(shape, values)
    assert python_array == replace(to_python_array(python_array))
