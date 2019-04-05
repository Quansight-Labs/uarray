import pytest

from uarray import TypeCheckBackend, MultiMethod, register_backend, deregister_backend, BackendNotImplementedError


class DummyClass:
    def __init__(self, other=None):
        pass


def dummy_fd(a):
    return (a,)


def dummy_rd(args, kwargs, rep_args):
    out_args = dummy_fd(*rep_args, **kwargs)
    out_kwargs = {}

    return out_args, out_kwargs


@pytest.fixture(scope='function')
def dummy_method(dummy_backend):
    return MultiMethod(dummy_fd, dummy_rd)


@pytest.fixture(scope='function')
def dummy_backend():
    backend = TypeCheckBackend((DummyClass,))
    register_backend(backend)
    yield backend
    deregister_backend(backend)


def test_normal(dummy_backend, dummy_method):
    implementation_called = [False]

    def implementation(method, args, kwargs):
        implementation_called[0] = True

    dummy_backend.register_method(dummy_method, implementation)
    dummy_method(DummyClass())

    assert implementation_called[0]


def test_invalidtype(dummy_method):
    class InvalidClass:
        pass

    with pytest.raises(BackendNotImplementedError):
        dummy_method(InvalidClass())


def test_invalidmethod():
    invalid_method = MultiMethod(dummy_fd, dummy_rd)

    with pytest.raises(BackendNotImplementedError):
        invalid_method(DummyClass())


def test_method_repr(dummy_method):
    assert str(dummy_fd) == str(dummy_method)
    assert repr(dummy_fd) == repr(dummy_method)


def test_subclasses(dummy_backend, dummy_method):
    class InheritedClass(DummyClass):
        pass

    def implementation(method, args, kwargs):
        pass

    dummy_backend.register_method(dummy_method, implementation)
    dummy_method(InheritedClass())
    dummy_backend.__init__((DummyClass,), allow_subclasses=False)

    with pytest.raises(BackendNotImplementedError):
        dummy_method(InheritedClass())


def test_method_notimplemented(dummy_backend, dummy_method):
    def implementation(method, args, kwargs):
        return NotImplemented

    dummy_backend.register_method(dummy_method, implementation)

    with pytest.raises(BackendNotImplementedError):
        dummy_method(DummyClass())
