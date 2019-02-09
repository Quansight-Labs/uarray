from .dispatch import *
from .moa import *
from .core import *
from .nested_sequence import *


def test_isomoprhic():
    shape = (2, 2)
    values = (1, 2), (3, 4)
    python_array = create_python_array(shape, values)
    assert python_array == replace(to_python_array(python_array))


def test_binary_operation():
    a = MoA.from_array(create_python_array((2, 2), ((1, 2), (3, 4))))
    assert replace(
        a.binary_operation(
            create_python_bin_abs(lambda l, r: l + r, int, int), a
        ).array[Array.create_shape(Nat(0), Nat(0))]
    ) == Box(2)
