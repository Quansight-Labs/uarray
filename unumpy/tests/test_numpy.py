import pytest

import uarray as ua
import unumpy as np
from unumpy.numpy_backend import NumpyBackend
from unumpy.pytorch_backend import TorchBackend


@pytest.fixture(scope='session', params=[NumpyBackend, TorchBackend])
def backend_type(request):
    backend = request.param
    return (backend, backend.types[0])


@pytest.mark.parametrize('method, args, kwargs', [
    (np.add, ([1], [2]), {}),  # type: ignore
    (np.sin, ([1.0],), {}),  # type: ignore
    (np.arange, (5, 20, 5), {},)
])
def test_functions(backend_type, method, args, kwargs):
    backend, ret_type = backend_type
    with ua.set_backend(backend, coerce=True):
        ret = method(*args, **kwargs)
        assert isinstance(ret, ret_type)
