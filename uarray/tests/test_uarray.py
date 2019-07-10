import uarray as ua
import pickle


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
def _extractor():
    return ()


def test_pickle_support():
    mm = _extractor
    state = mm.__getstate__()

    s = pickle.dumps(mm)
    mm_unpickled = pickle.loads(s)

    assert mm_unpickled.__getstate__() == state
