import pytest

from uarray.backend import TypeCheckBackend, Method, register_backend, deregister_backend


class DummyClass:
    def __init__(self, other=None):
        pass


def dummy_fd(a):
    return (a,)


def dummy_rd(args, kwargs, rep_args):
    out_args = dummy_fd(*rep_args, **kwargs)
    out_kwargs = {}

    return out_args, out_kwargs


dummy_method = Method(dummy_fd, dummy_rd)

dummy_backend = TypeCheckBackend((DummyClass,), DummyClass)


def setup_module():
    register_backend(dummy_backend)


def teardown_module():
    deregister_backend(dummy_backend)


def test_normal():
    implementation_called = [False]

    def implementation(method, args, kwargs):
        implementation_called[0] = True

    dummy_backend.register_method(dummy_method, implementation)

    try:
        dummy_method(DummyClass())
    finally:
        dummy_backend.deregister_method(dummy_method)

    assert implementation_called[0]


def test_invalidtype():
    class InvalidClass:
        pass

    with pytest.raises(TypeError):
        dummy_method(InvalidClass())


def test_invalidmethod():
    invalid_method = Method(dummy_fd, dummy_rd)

    with pytest.raises(TypeError):
        invalid_method(DummyClass())


def test_method_repr():
    assert str(dummy_fd) == str(dummy_method)
    assert repr(dummy_fd) == repr(dummy_method)


def test_subclasses():
    class InheritedClass(DummyClass):
        pass

    def implementation(method, args, kwargs):
        pass

    dummy_backend.register_method(dummy_method, implementation)

    try:
        dummy_method(InheritedClass())
        dummy_backend.allow_subclasses = False

        with pytest.raises(TypeError):
            dummy_method(InheritedClass())
    finally:
        dummy_backend.allow_subclasses = True
        dummy_backend.deregister_method(dummy_method)


def test_method_notimplemented():
    def implementation(method, args, kwargs):
        return NotImplemented

    try:
        dummy_backend.register_method(dummy_method, implementation)

        with pytest.raises(TypeError):
            dummy_method(DummyClass())
    finally:
        dummy_backend.deregister_method(dummy_method)
