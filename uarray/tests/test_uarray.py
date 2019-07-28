import uarray as ua
import pickle

import pytest  # type: ignore


@pytest.fixture(scope="function")
def cleanup_backends(request):
    def cleanup():
        ua.clear_backends("ua_tests", registered=True, globals=True)

    request.addfinalizer(cleanup)


class Backend:
    __ua_domain__ = "ua_tests"


def test_nestedbackend():
    obj = object()
    be_outer = Backend()
    be_outer.__ua_function__ = lambda f, a, kw: obj

    mm1 = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    def default(*a, **kw):
        return mm1(*a, **kw)

    mm2 = ua.generate_multimethod(
        lambda: (), lambda a, kw, d: (a, kw), "ua_tests", default=default
    )

    be_inner = Backend()

    def be2_ua_func(f, a, kw):
        with ua.skip_backend(be_inner):
            return f(*a, **kw)

    be_inner.__ua_function__ = be2_ua_func
    with ua.set_backend(be_outer), ua.set_backend(be_inner):
        assert mm2() is obj


def _replacer(args, kwargs, dispatchables):
    return (args, kwargs)


@ua.create_multimethod(_replacer, "ua_tests")
def pickle_mm():
    return ()


def test_pickle_support():
    unpickle_mm = pickle.loads(pickle.dumps(pickle_mm))

    assert unpickle_mm is pickle_mm


def test_registration(cleanup_backends):
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj
    mm = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    ua.register_backend(be)
    assert mm() is obj


def test_global(cleanup_backends):
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj
    mm = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    ua.set_global_backend(be)
    assert mm() is obj


def ctx_before_global(cleanup_backends):
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2
    mm = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    ua.set_global_backend(be)

    with ua.set_backend(be2):
        assert mm() is obj2


def test_global_before_registered(cleanup_backends):
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2
    mm = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    ua.set_global_backend(be)
    ua.register_backend(be2)
    assert mm() is obj


def test_global_only(cleanup_backends):
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: NotImplemented

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj
    mm = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    ua.set_global_backend(be, only=True)
    ua.register_backend(be2)

    with pytest.raises(ua.BackendNotImplementedError):
        mm()


def test_clear_backends(cleanup_backends):
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2
    mm = ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")

    ua.set_global_backend(be)
    ua.register_backend(be2)

    ua.clear_backends(Backend.__ua_domain__, registered=True, globals=True)
    with pytest.raises(ua.BackendNotImplementedError):
        mm()
