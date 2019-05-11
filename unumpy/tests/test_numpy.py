import pytest
import uarray as ua
import unumpy as np
import numpy as onp
import torch
import xnd
import dask.array as da
import sparse
import unumpy.numpy_backend as NumpyBackend

# from unumpy.torch_backend import TorchBackend
import unumpy.xnd_backend as XndBackend
import unumpy.dask_backend as DaskBackend
import unumpy.sparse_backend as SparseBackend

LIST_BACKENDS = [
    (NumpyBackend, (onp.ndarray, onp.generic)),
    pytest.param(
        (XndBackend, xnd.xnd), marks=pytest.mark.xfail(reason="Xnd currently broken.")
    ),
    (DaskBackend, (da.core.Array, onp.generic)),
    (SparseBackend, (sparse.SparseArray, onp.generic)),
]

try:
    import unumpy.cupy_backend as CupyBackend
    import cupy as cp

    LIST_BACKENDS.append(pytest.param((CupyBackend, (cp.ndarray, cp.generic))))
except ImportError:
    pass


FULLY_TESTED_BACKENDS = (NumpyBackend, XndBackend, DaskBackend)

EXCEPTIONS = {
    (DaskBackend, np.in1d),
    (DaskBackend, np.intersect1d),
    (DaskBackend, np.setdiff1d),
    (DaskBackend, np.setxor1d),
    (DaskBackend, np.union1d),
    (DaskBackend, np.sort),
    (DaskBackend, np.lexsort),
}


@pytest.fixture(scope="session", params=LIST_BACKENDS)
def backend(request):
    backend = request.param
    return backend


@pytest.mark.parametrize(
    "method, args, kwargs",
    [
        (np.add, ([1], [2]), {}),  # type: ignore
        (np.sin, ([1.0],), {}),  # type: ignore
        (np.arange, (5, 20, 5), {}),
    ],
)
def test_ufuncs_coerce(backend, method, args, kwargs):
    backend, types = backend
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend in FULLY_TESTED_BACKENDS:
            raise
        pytest.xfail(reason="The backend has no implementation for this ufunc.")

    assert isinstance(ret, types)


def replace_args_kwargs(method, backend, args, kwargs):
    instance = ()
    while not hasattr(method, "_coerce_args"):
        instance += (method,)
        method = method.__call__

        if method is method.__call__:
            raise ValueError("Nowhere up the chain is there a multimethod.")

    args, kwargs, *_ = method._coerce_args(
        backend, instance + args, kwargs, coerce=True
    )
    return args[len(instance) :], kwargs


@pytest.mark.parametrize(
    "method, args, kwargs",
    [
        (np.sum, ([1],), {}),
        (np.prod, ([1.0],), {}),
        (np.any, ([True, False],), {}),
        (np.all, ([True, False],), {}),
        (np.min, ([1, 3, 2],), {}),
        (np.max, ([1, 3, 2],), {}),
        (np.argmin, ([1, 3, 2],), {}),
        (np.argmax, ([1, 3, 2],), {}),
        (np.nanmin, ([1, 3, 2],), {}),
        (np.nanmax, ([1, 3, 2],), {}),
        (np.std, ([1, 3, 2],), {}),
        (np.var, ([1, 3, 2],), {}),
        (np.unique, ([1, 2, 2],), {}),
        (np.in1d, ([1], [1, 2, 2]), {}),
        (np.isin, ([1], [1, 2, 2]), {}),
        (np.intersect1d, ([1, 3, 4, 3], [3, 1, 2, 1]), {}),
        (np.setdiff1d, ([1, 3, 4, 3], [3, 1, 2, 1]), {}),
        (np.setxor1d, ([1, 3, 4, 3], [3, 1, 2, 1]), {}),
        (np.sort, ([3, 1, 2, 4],), {}),
        pytest.param(
            np.lexsort,
            (([1, 2, 2, 3], [3, 1, 2, 1]),),
            {},
            marks=pytest.mark.xfail(reason="Lexsort doesn't fully work for CuPy."),
        ),
        (np.stack, (([1, 2], [3, 4]),), {}),
        (np.concatenate, (([1, 2, 3], [3, 4]),), {}),
        (np.broadcast_to, ([1, 2], (2, 2)), {}),
    ],
)
def test_functions_coerce(backend, method, args, kwargs):
    backend, types = backend
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend in FULLY_TESTED_BACKENDS and (backend, method) not in EXCEPTIONS:
            raise
        pytest.xfail(reason="The backend has no implementation for this ufunc.")

    assert isinstance(ret, types)


@pytest.mark.parametrize(
    "method, args, kwargs", [(np.broadcast_arrays, ([1, 2], [[3, 4]]), {})]
)
def test_multiple_output(backend, method, args, kwargs):
    backend, types = backend
    try:
        with ua.set_backend(backend, coerce=True):
            ret = method(*args, **kwargs)
    except ua.BackendNotImplementedError:
        if backend in FULLY_TESTED_BACKENDS and (backend, method) not in EXCEPTIONS:
            raise
        pytest.xfail(reason="The backend has no implementation for this ufunc.")

    assert all(isinstance(arr, types) for arr in ret)
