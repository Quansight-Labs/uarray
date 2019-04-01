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
])
def test_ufuncs_coerce(backend, method, args, kwargs):
    try:
        ret_type = backend.types[0]
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
            assert isinstance(ret, ret_type)
    except ua.BackendNotImplementedError:
        if backend is NumpyBackend:
            raise
        pytest.xfail(reason='The backend has no implementation for this ufunc.')


@pytest.mark.parametrize('method, args, kwargs', [
    (np.add, ([1], [2]), {}),  # type: ignore
    (np.sin, ([1.0],), {}),  # type: ignore
    (np.arange, (5, 20, 5), {},)
])
def test_functions(backend, method, args, kwargs):
    ret_type = backend.types[0]
    args_new, kwargs_new = replace_args_kwargs(method, backend, args, kwargs)
    ret = method(*args_new, **kwargs_new)

    if all((a is b for a, b in zip(args, args_new))) and kwargs.keys() == kwargs_new.keys() and \
            all((kwargs[k] is kwargs_new[k] for k in kwargs)):
        pytest.xfail(reason='No arguments replaced, this is probably an array creation function. '
                            'Creation functions only supported when a backend is set.')

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
