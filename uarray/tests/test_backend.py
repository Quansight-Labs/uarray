import pytest

import uarray as ua


class DummyClass:
    def __init__(self, other=None):
        pass


def dummy_fd(a):
    return (a,)


def dummy_rd(args, kwargs, rep_args):
    out_args = dummy_fd(*rep_args, **kwargs)
    out_kwargs = {}

    return out_args, out_kwargs


@pytest.fixture(scope="function")
def dummy_method(dummy_backend):
    return ua.MultiMethod(dummy_fd, dummy_rd)


@pytest.fixture(scope="function")
def dummy_backend():
    backend = ua.Backend()
    with ua.set_backend(backend):
        yield backend


def test_normal(dummy_backend, dummy_method):
    implementation_called = [False]

    def implementation(method, args, kwargs, dispatchable_args):
        implementation_called[0] = True

    dummy_backend.register_implementation(dummy_method, implementation)
    dummy_method(DummyClass())

    assert implementation_called[0]


def test_invalidmethod():
    invalid_method = ua.MultiMethod(dummy_fd, dummy_rd)

    with pytest.raises(ua.BackendNotImplementedError):
        invalid_method(DummyClass())


def test_method_repr(dummy_method):
    assert str(dummy_fd) == str(dummy_method)
    assert repr(dummy_fd) == repr(dummy_method)


def test_method_notimplemented(dummy_backend, dummy_method):
    def implementation(method, args, kwargs, dispatchable_args):
        return NotImplemented

    dummy_backend.register_implementation(dummy_method, implementation)

    with pytest.raises(ua.BackendNotImplementedError):
        dummy_method(DummyClass())
