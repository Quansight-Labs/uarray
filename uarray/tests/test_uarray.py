import uarray as ua
import pickle

import pytest  # type: ignore


@pytest.fixture(scope="function", autouse=True)
def cleanup_backends():
    """
    Cleanup backends

    Args:
    """
    with ua.reset_state():
        yield


class Backend:
    __ua_domain__ = "ua_tests"


class DisableBackend:
    def __init__(self, domain="ua_tests"):
        """
        Initialize the domain.

        Args:
            self: (todo): write your description
            domain: (str): write your description
        """
        self.__ua_domain__ = domain
        self.active = True
        self.ret = object()

    def __ua_function__(self, f, a, kw):
        """
        Return the result of a function.

        Args:
            self: (todo): write your description
            f: (todo): write your description
            a: (todo): write your description
            kw: (todo): write your description
        """
        if self.active:
            return self.ret

        raise ua.BackendNotImplementedError(self.__ua_domain__)


@pytest.fixture()
def nullary_mm():
    """
    Generate null null null version 1d arrays.

    Args:
    """
    return ua.generate_multimethod(lambda: (), lambda a, kw, d: (a, kw), "ua_tests")


def test_nestedbackend(nullary_mm):
    """
    Test if a_mm is a nested function.

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    be_outer = Backend()
    be_outer.__ua_function__ = lambda f, a, kw: obj

    def default(*a, **kw):
        """
        Default factory function that returns the default value.

        Args:
            a: (todo): write your description
            kw: (todo): write your description
        """
        return nullary_mm(*a, **kw)

    mm2 = ua.generate_multimethod(
        lambda: (), lambda a, kw, d: (a, kw), "ua_tests", default=default
    )
    be_inner = Backend()

    def be2_ua_func(f, a, kw):
        """
        Beamplemented function f ( f )

        Args:
            f: (todo): write your description
            a: (todo): write your description
            kw: (todo): write your description
        """
        with ua.skip_backend(be_inner):
            return f(*a, **kw)

    be_inner.__ua_function__ = be2_ua_func
    with ua.set_backend(be_outer), ua.set_backend(be_inner):
        assert mm2() is obj


def _replacer(args, kwargs, dispatchables):
    """
    Decorator to injectables.

    Args:
        dispatchables: (str): write your description
    """
    return (args, kwargs)


@ua.create_multimethod(_replacer, "ua_tests")
def pickle_mm():
    """
    Pickle_mm of all possible picklemm ).

    Args:
    """
    return ()


def test_pickle_support():
    """
    Test if pickle is a pickle.

    Args:
    """
    unpickle_mm = pickle.loads(pickle.dumps(pickle_mm))

    assert unpickle_mm is pickle_mm


def test_registration(nullary_mm):
    """
    Test if the registration.

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    ua.register_backend(be)
    assert nullary_mm() is obj


def test_global(nullary_mm):
    """
    Test if the global global global.

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    ua.set_global_backend(be)
    assert nullary_mm() is obj


def ctx_before_global(nullary_mm):
    """
    Ctx global global global global function.

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2

    ua.set_global_backend(be)

    with ua.set_backend(be2):
        assert nullary_mm() is obj2


def test_global_before_registered(nullary_mm):
    """
    Test if the global global global

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2

    ua.set_global_backend(be)
    ua.register_backend(be2)
    assert nullary_mm() is obj


def test_global_try_last(nullary_mm):
    """
    Test if the last call

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    obj2 = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: obj

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj2

    ua.set_global_backend(be, try_last=True)
    ua.register_backend(be2)
    assert nullary_mm() is obj2


def test_global_only(nullary_mm):
    """
    Test if the global test.

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: NotImplemented

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: obj

    ua.set_global_backend(be, only=True)
    ua.register_backend(be2)

    with pytest.raises(ua.BackendNotImplementedError):
        nullary_mm()


def test_clear_backends(nullary_mm):
    """
    Clear all backends

    Args:
        nullary_mm: (todo): write your description
    """
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


def test_function_attrs():
    """
    Extractor function.

    Args:
    """
    def extractor():
        """
        Extracts a list of this function that.

        Args:
        """
        return ()

    def replacer(a, kw, d):
        """
        Replacer a function that d d.

        Args:
            a: (array): write your description
            kw: (todo): write your description
            d: (array): write your description
        """
        return a, kw

    def default():
        """
        Return the default value.

        Args:
        """
        return NotImplemented

    mm = ua.generate_multimethod(extractor, replacer, "ua_tests", default=default)

    assert mm.arg_extractor is extractor
    assert mm.arg_replacer is replacer
    assert mm.default is default
    assert mm.domain == "ua_tests"


def test_raising_from_backend(nullary_mm):
    """
    Test if the backend is a 3doo.

    Args:
        nullary_mm: (bool): write your description
    """
    def raise_(foo):
        """
        Checks if the given iterator.

        Args:
            foo: (todo): write your description
        """
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


def test_nested():
    """
    Test if nested nested nested nested nested nested directories.

    Args:
    """
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: None

    ctx = ua.set_backend(be)

    with ctx, ctx:
        pass


def test_invalid():
    """
    Test if the current state that will be run.

    Args:
    """
    be1 = Backend()
    be1.__ua_function__ = lambda f, a, kw: None

    be2 = Backend()
    be2.__ua_function__ = lambda f, a, kw: None

    ctx1 = ua.set_backend(be1)
    ctx2 = ua.set_backend(be2)

    with pytest.raises(RuntimeError):
        try:
            ctx1.__enter__()
            try:
                ctx2.__enter__()
            finally:
                ctx1.__exit__(None, None, None)
        finally:
            ctx2.__exit__(None, None, None)


def test_skip_comparison(nullary_mm):
    """
    Decorator todo that the wrapped functions.

    Args:
        nullary_mm: (bool): write your description
    """
    be1 = Backend()
    be1.__ua_function__ = lambda f, a, kw: None

    class Backend2(Backend):
        @staticmethod
        def __ua_function__(f, a, kw):
            """
            Decor function decorators a function.

            Args:
                f: (todo): write your description
                a: (todo): write your description
                kw: (todo): write your description
            """
            pass

        def __eq__(self, other):
            """
            Determine whether two values are equal.

            Args:
                self: (todo): write your description
                other: (todo): write your description
            """
            return other is self or other is be1

    with pytest.raises(ua.BackendNotImplementedError):
        with ua.set_backend(be1), ua.skip_backend(Backend2()):
            nullary_mm()


def test_skip_raises(nullary_mm):
    """
    Decorator tomodified cross - validation.

    Args:
        nullary_mm: (bool): write your description
    """
    be1 = Backend()
    be1.__ua_function__ = lambda f, a, kw: None

    foo = Exception("Foo")

    class Backend2(Backend):
        @staticmethod
        def __ua_function__(f, a, kw):
            """
            Decor function decorators a function.

            Args:
                f: (todo): write your description
                a: (todo): write your description
                kw: (todo): write your description
            """
            pass

        def __eq__(self, other):
            """
            Determine if the given object is equal todo.

            Args:
                self: (todo): write your description
                other: (todo): write your description
            """
            raise foo

    with pytest.raises(Exception) as e:
        with ua.set_backend(be1), ua.skip_backend(Backend2()):
            nullary_mm()

    assert e.value is foo


def test_getset_state(cleanup_backends):
    """
    Test if the global state.

    Args:
        cleanup_backends: (todo): write your description
    """
    ua.set_global_backend(Backend())
    ua.register_backend(Backend())

    with ua.set_backend(Backend()), ua.skip_backend(Backend()):
        state = ua.get_state()

    pstate = state._pickle()

    assert pstate != ua.get_state()._pickle()

    with ua.set_state(state):
        assert pstate[:2] == ua.get_state()._pickle()[:2]


class ComparableBackend(Backend):
    def __init__(self, obj):
        """
        Initialize the object.

        Args:
            self: (todo): write your description
            obj: (todo): write your description
        """
        super().__init__()
        self.obj = obj

    def __eq__(self, other):
        """
        Determine if two values are equal.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return isinstance(other, ComparableBackend) and self.obj == other.obj

    def __ne__(self, other):
        """
        Returns true if self is a and false otherwise.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return not (self == other)


def test_pickle_state():
    """
    Perform state of the global.

    Args:
    """
    ua.set_global_backend(ComparableBackend("a"))
    ua.register_backend(ComparableBackend("b"))

    with ua.set_backend(ComparableBackend("c")), ua.skip_backend(
        ComparableBackend("d")
    ):
        state = ua.get_state()

    state_loaded = pickle.loads(pickle.dumps(state))

    assert state._pickle() == state_loaded._pickle()


def test_hierarchical_backends():
    """
    Generate backends.

    Args:
    """
    mm = ua.generate_multimethod(
        lambda: (), lambda a, kw, d: (a, kw), "ua_tests.foo.bar"
    )
    subdomains = "ua_tests.foo.bar".split(".")
    depth = len(subdomains)

    mms = [
        ua.generate_multimethod(
            lambda: (), lambda a, kw, d: (a, kw), ".".join(subdomains[: i + 1])
        )
        for i in range(depth)
    ]

    be = [DisableBackend(".".join(subdomains[: i + 1])) for i in range(depth)]

    ua.set_global_backend(be[1])
    with pytest.raises(ua.BackendNotImplementedError):
        mms[0]()

    for i in range(1, depth):
        assert mms[i]() is be[1].ret

    ua.set_global_backend(be[0])

    for i in range(depth):
        assert mms[i]() is be[min(i, 1)].ret

    ua.set_global_backend(be[2])

    for i in range(depth):
        assert mms[i]() is be[i].ret

    be[2].active = False
    for i in range(depth):
        print(i)
        assert mms[i]() is be[min(i, 1)].ret

    be[1].active = False
    for i in range(depth):
        assert mms[i]() is be[0].ret

    be[0].active = False
    for i in range(depth):
        with pytest.raises(ua.BackendNotImplementedError):
            mms[i]()

    # only=True prevents all further domain checking
    be[0].active = True
    be[1].active = True
    with ua.set_backend(be[2], only=True), pytest.raises(ua.BackendNotImplementedError):
        mms[2]()


def test_multidomain_backends():
    """
    Generate a multidom algorithm.

    Args:
    """
    n_domains = 2
    be = DisableBackend(domain=["ua_tests" + str(i) for i in range(n_domains)])

    mms = [
        ua.generate_multimethod(
            lambda: (), lambda a, kw, d: (a, kw), "ua_tests" + str(i)
        )
        for i in range(n_domains)
    ]

    def assert_no_backends():
        """
        Asserts that the backends are backends.

        Args:
        """
        for i in range(len(mms)):
            with pytest.raises(ua.BackendNotImplementedError):
                mms[i]()

    def assert_backend_active(backend):
        """
        Check if all backend is active.

        Args:
            backend: (str): write your description
        """
        assert all(mms[i]() is backend.ret for i in range(len(mms)))

    assert_no_backends()

    with ua.set_backend(be):
        assert_backend_active(be)

    ua.set_global_backend(be)
    assert_backend_active(be)

    with ua.skip_backend(be):
        assert_no_backends()

    assert_backend_active(be)

    for i in range(len(mms)):
        ua.clear_backends(mms[i].domain, globals=True)

        with pytest.raises(ua.BackendNotImplementedError):
            mms[i]()

        for j in range(i + 1, len(mms)):
            assert mms[j]() is be.ret

    assert_no_backends()

    ua.register_backend(be)
    assert_backend_active(be)


def test_determine_backend(nullary_mm):
    """
    Determine ifend of the backend. backend.

    Args:
        nullary_mm: (todo): write your description
    """
    class TypeA:
        pass

    class TypeB:
        pass

    mark = "determine_backend_test"

    class TypeBackend:
        __ua_domain__ = "ua_tests"

        def __init__(self, my_type):
            """
            Initialize a new type.

            Args:
                self: (todo): write your description
                my_type: (todo): write your description
            """
            self.my_type = my_type

        def __ua_convert__(self, dispatchables, coerce):
            """
            Convert all of the given type to a dimtype.

            Args:
                self: (todo): write your description
                dispatchables: (str): write your description
                coerce: (str): write your description
            """
            if not all(
                type(d.value) is self.my_type and d.type is mark for d in dispatchables
            ):
                return NotImplemented
            return tuple(d.value for d in dispatchables)

        def __ua_function__(self, func, args, kwargs):
            """
            Returns a function of the given function.

            Args:
                self: (todo): write your description
                func: (todo): write your description
            """
            return self.my_type

    BackendA = TypeBackend(TypeA)
    BackendB = TypeBackend(TypeB)

    with ua.set_backend(BackendA), pytest.raises(ua.BackendNotImplementedError):
        with ua.determine_backend(TypeB(), mark, domain="ua_tests"):
            pass

    with ua.set_backend(BackendA), ua.set_backend(BackendB):
        with ua.determine_backend(TypeA(), mark, domain="ua_tests"):
            assert nullary_mm() is TypeA

        with ua.determine_backend(TypeB(), mark, domain="ua_tests"):
            assert nullary_mm() is TypeB

    # Has no __ua_convert__, so assumed to not accept the type
    with ua.set_backend(DisableBackend()), pytest.raises(ua.BackendNotImplementedError):
        with ua.determine_backend(TypeB(), mark, domain="ua_tests"):
            pass

    with ua.set_backend(BackendA), ua.set_backend(BackendB):
        with pytest.raises(ua.BackendNotImplementedError):
            with ua.determine_backend_multi(
                [ua.Dispatchable(TypeA(), mark), ua.Dispatchable(TypeB(), mark)],
                domain="ua_tests",
            ):
                pass

        with ua.determine_backend_multi(
            [ua.Dispatchable(TypeA(), mark), ua.Dispatchable(TypeA(), mark)],
            domain="ua_tests",
        ):
            assert nullary_mm() is TypeA


def test_determine_backend_coerce(nullary_mm):
    """
    Determine whether the backend can be a subclass of backendables.

    Args:
        nullary_mm: (todo): write your description
    """
    class TypeA:
        pass

    class TypeB:
        pass

    mark = "determine_backend_test"

    class TypeBackend:
        __ua_domain__ = "ua_tests"

        def __init__(self, my_type):
            """
            Initialize a new type.

            Args:
                self: (todo): write your description
                my_type: (todo): write your description
            """
            self.my_type = my_type

        def __ua_convert__(self, dispatchables, coerce):
            """
            Determine whether or notmarkables type.

            Args:
                self: (todo): write your description
                dispatchables: (str): write your description
                coerce: (str): write your description
            """
            if len(dispatchables) > 0:
                print(dispatchables[0], coerce)
            if coerce and all(d.coercible for d in dispatchables):
                return tuple(self.my_type() for _ in dispatchables)

            if not all(
                type(d.value) is self.my_type and d.type is mark for d in dispatchables
            ):
                return NotImplemented
            return tuple(d.value for d in dispatchables)

        def __ua_function__(self, func, args, kwargs):
            """
            Returns a function of the given function.

            Args:
                self: (todo): write your description
                func: (todo): write your description
            """
            return self.my_type

    BackendA = TypeBackend(TypeA)
    BackendB = TypeBackend(TypeB)
    unary_mm = ua.generate_multimethod(
        lambda a: (ua.Dispatchable(a, mark),), lambda a, kw, d: (d, kw), "ua_tests"
    )

    # coercion is not forced on the existing set backend
    with ua.set_backend(BackendA), ua.set_backend(BackendB):
        with ua.determine_backend(TypeA(), mark, domain="ua_tests", coerce=True):
            assert nullary_mm() is TypeA
            assert unary_mm(TypeB()) is TypeA

    # But is allowed if the backend was set with coerce in the first place
    with ua.set_backend(BackendA), ua.set_backend(BackendB, coerce=True):
        with ua.determine_backend(TypeA(), mark, domain="ua_tests", coerce=True):
            assert nullary_mm() is TypeB
            assert unary_mm(TypeA()) is TypeB


def test_default(nullary_mm):
    """
    Default test test.

    Args:
        nullary_mm: (bool): write your description
    """
    obj = object()
    be = Backend()
    be.__ua_function__ = lambda f, a, kw: NotImplemented

    # If a backend returns NotImplemented, the default is called
    def default1(*a, **kw):
        """
        Return a default value.

        Args:
            a: (todo): write your description
            kw: (todo): write your description
        """
        return obj

    mm1 = ua.generate_multimethod(
        lambda: (), lambda a, kw, d: (a, kw), "ua_tests", default=default1
    )

    with ua.set_backend(be):
        assert mm1() is obj

    # If all backends fail, the default is called again without a specific backend
    num_calls = [0]

    def default2(*a, **kw):
        """
        Convenience function.

        Args:
            a: (todo): write your description
            kw: (todo): write your description
        """
        num_calls[0] = num_calls[0] + 1
        raise ua.BackendNotImplementedError()

    mm2 = ua.generate_multimethod(
        lambda: (), lambda a, kw, d: (a, kw), "ua_tests", default=default2
    )

    with ua.set_backend(be), pytest.raises(ua.BackendNotImplementedError):
        mm2()

    assert num_calls[0] == 2

    # If the last backend is set as only or coerce, the last default call is skipped
    num_calls[0] = 0
    with ua.set_backend(be, only=True), pytest.raises(ua.BackendNotImplementedError):
        mm2()
    assert num_calls[0] == 1
    num_calls[0] = 0
    with ua.set_backend(be, coerce=True), pytest.raises(ua.BackendNotImplementedError):
        mm2()
    assert num_calls[0] == 1
