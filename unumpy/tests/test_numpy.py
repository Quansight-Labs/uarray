import numpy as np
import unumpy as unp


def test_add():
    assert unp.add.nin == np.add.nin
    assert isinstance(unp.add(np.asarray([5]), [6]), np.ndarray)
