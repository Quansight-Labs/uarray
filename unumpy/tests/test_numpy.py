import pytest

import uarray as ua
import unumpy as np
import numpy as onp
import torch
import xnd
from unumpy.numpy_backend import NumpyBackend
from unumpy.torch_backend import TorchBackend
from unumpy.xnd_backend import XndBackend


@pytest.fixture(scope='session', params=[
    (NumpyBackend, (onp.ndarray, onp.generic)),
    (TorchBackend, torch.Tensor),
    (XndBackend, xnd.xnd),
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
    backend, types = backend
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend in (NumpyBackend, XndBackend):
            raise
        pytest.xfail(reason='The backend has no implementation for this ufunc.')

    assert isinstance(ret, types)


@pytest.mark.parametrize('method, args, kwargs', [
    (np.add, ([1], [2]), {}),  # type: ignore
    (np.sin, ([1.0],), {}),  # type: ignore
])
def test_functions(backend, method, args, kwargs):
    backend, types = backend
    args_new, kwargs_new = replace_args_kwargs(method, backend, args, kwargs)
    ret = method(*args_new, **kwargs_new)
    assert isinstance(ret, types)


def replace_args_kwargs(method, backend, args, kwargs):
    while not isinstance(method, (ua.MultiMethod, ua.BoundMultiMethod)):
        method = method.__call__

        if method is method.__call__:
            raise ValueError("Nowhere up the chain is there a multimethod.")

    instance = ()
    while isinstance(method, ua.BoundMultiMethod):
        instance += (method.instance,)
        method = method.method

    args, kwargs, *_ = backend.replace_dispatchables(method, instance + args, kwargs, coerce=True)
    return args[len(instance):], kwargs


@pytest.mark.parametrize('method, args, kwargs', [
    (np.sum, ([1],), {}),
    (np.prod, ([1.0],), {}),
    (np.any, ([True, False],), {}),
    (np.all, ([True, False],), {}),
    (np.min, ([1, 3, 2],), {}),
    (np.max, ([1, 3, 2],), {}),
    (np.argmin, ([1, 3, 2],), {}),
    (np.argmax, ([1, 3, 2],), {}),
])
def test_ufunc_reductions(backend, method, args, kwargs):
    backend, types = backend
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend in (NumpyBackend, XndBackend):
            raise
        pytest.xfail(reason='The backend has no implementation for this ufunc.')

    assert isinstance(ret, types)
