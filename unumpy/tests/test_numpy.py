import pytest

import uarray as ua
import unumpy as np
from unumpy.numpy_backend import NumpyBackend
from unumpy.pytorch_backend import TorchBackend
from unumpy.xnd_backend import XndBackend


@pytest.fixture(scope='session', params=[
    NumpyBackend,
    TorchBackend,
    XndBackend,
])
def backend(request):
    backend = request.param
    return backend


@pytest.mark.parametrize('method, args, kwargs', [
    (np.add, ([1], [2]), {}),  # type: ignore
    (np.sin, ([1.0],), {}),  # type: ignore
    (np.arange, (5, 20, 5), {},)
])
def test_ufuncs_coerce(backend, method, args, kwargs):
    ret_type = backend.types
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend is NumpyBackend:
            raise
        pytest.xfail(reason='The backend has no implementation for this ufunc.')

    assert isinstance(ret, ret_type)


@pytest.mark.parametrize('method, args, kwargs', [
    (np.add, ([1], [2]), {}),  # type: ignore
    (np.sin, ([1.0],), {}),  # type: ignore
])
def test_functions(backend, method, args, kwargs):
    ret_type = backend.types
    args_new, kwargs_new = replace_args_kwargs(method, backend, args, kwargs)
    ret = method(*args_new, **kwargs_new)
    assert isinstance(ret, ret_type)


def replace_args_kwargs(method, backend, args, kwargs):
    instance = ()
    while not isinstance(method, ua.MultiMethod):
        if method.__call__ is method:
            raise TypeError('Nowhere up the chain was there a MultiMethod.')

        instance = (method,)
        method = method.__call__

    args, kwargs = method.replace_arrays(backend, instance + args, kwargs)
    return args[len(instance):], kwargs


@pytest.mark.parametrize('method, args, kwargs', [
    (np.sum, ([1],), {}),
    (np.prod, ([1.0],), {}),
    (np.any, ([True, False],), {}),
    (np.all, ([True, False],), {}),
    (np.min, ([1, 3, 2],), {}),
    (np.max, ([1, 3, 2],), {}),
])
def test_ufunc_reductions(backend, method, args, kwargs):
    ret_type = backend.types
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend is NumpyBackend:
            raise
        pytest.xfail(reason='The backend has no implementation for this ufunc.')

    assert isinstance(ret, ret_type)
