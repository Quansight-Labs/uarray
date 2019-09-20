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


@pytest.fixture()
def nullary_mm():
    return ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")


def test_nestedbackend(nullary_mm):
    obj = object()
    be_outer = Backend()
    be_outer.__ua_function__ = lambda f, a, kw: obj

    def default(*a, **kw):
        return nullary_mm(*a, **kw)

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


def test_registration(cleanup_backends, nullary_mm):
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    ua.register_backend(be)
    assert nullary_mm() is obj


def test_global(cleanup_backends, nullary_mm):
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    ua.set_global_backend(be)
    assert nullary_mm() is obj


def ctx_before_global(cleanup_backends, nullary_mm):
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2

    ua.set_global_backend(be)

    with ua.set_backend(be2):
        assert nullary_mm() is obj2


def test_global_before_registered(cleanup_backends, nullary_mm):
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2

    ua.set_global_backend(be)
    ua.register_backend(be2)
    assert nullary_mm() is obj


def test_global_only(cleanup_backends, nullary_mm):
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: NotImplemented

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj

    ua.set_global_backend(be, only=True)
    ua.register_backend(be2)

    with pytest.raises(ua.BackendNotImplementedError):
        nullary_mm()


def test_clear_backends(cleanup_backends, nullary_mm):
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2

    ua.set_global_backend(be)
    ua.register_backend(be2)

    ua.clear_backends(Backend.__ua_domain__, registered=True, globals=True)
    with pytest.raises(ua.BackendNotImplementedError):
        nullary_mm()


def test_get_extractor_replacer(cleanup_backends):
    def extractor():
        return ()

    def replacer(a, kw, d):
        return a, kw

    mm = ua.generate_multimethod(extractor, replacer, "ua_tests")

    assert mm.arg_extractor is extractor
    assert mm.arg_replacer is replacer


def test_raising_from_backend(nullary_mm):
    def raise_(foo):
        raise foo

    Foo = ua.BackendNotImplementedError("Foo")
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: raise_(Foo)

    # BackendNotImplementedErrors are nested
    with ua.set_backend(be):
        with pytest.raises(ua.BackendNotImplementedError) as e:
            nullary_mm()

        assert (
            e.value.args[0]
            == "No selected backends had an implementation for this function."
        )
        assert type(e.value.args[1]) == tuple
        assert e.value.args[1] == (be, Foo)

    Bar = ua.BackendNotImplementedError("Bar")
    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: raise_(Bar)
    # Errors are in the order the backends were tried
    with ua.set_backend(be), ua.set_backend(be2):
        with pytest.raises(ua.BackendNotImplementedError) as e:
            nullary_mm()

        assert e.value.args[1] == (be2, Bar)
        assert e.value.args[2] == (be, Foo)

    be3 = Backend()
    be3.__ua_function__ = lambda f, a, kw: "Success"
    # Can succeed after a backend has raised BackendNotImplementedError
    with ua.set_backend(be3), ua.set_backend(be):
        assert nullary_mm() == "Success"
