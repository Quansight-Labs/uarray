import uarray
from uarray.typing import _generate_arg_extractor_replacer, DispatchableArg
from typing import Optional


def example_function(a: int, b: float, c: Optional[str] = None):
    pass


EXAMPLE_ANNOTATIONS = (
    DispatchableArg("a", dispatch_type="int", coercible=True),
    DispatchableArg("b", dispatch_type="float", coercible=False),
)


def test_automatic_extractor():
    extractor, _ = _generate_arg_extractor_replacer(
        example_function, EXAMPLE_ANNOTATIONS
    )

    def validate_dispatchables(dispatchables, a, b):
        assert isinstance(dispatchables, tuple)
        assert len(dispatchables) == 2
        assert dispatchables[0].value is a
        assert dispatchables[0].type == "int"
        assert dispatchables[0].coercible == True

        assert dispatchables[1].value is b
        assert dispatchables[1].type == "float"
        assert dispatchables[1].coercible == False

    a, b = 1, 2.0
    validate_dispatchables(extractor(a, b), a, b)
    validate_dispatchables(extractor(a, b=b), a, b)
    validate_dispatchables(extractor(b=b, a=a), a, b)
    validate_dispatchables(extractor(c="c", a=a, b=b), a, b)
    validate_dispatchables(extractor(a, b, "c"), a, b)


def test_automatic_replacer():
    _, replacer = _generate_arg_extractor_replacer(
        example_function, EXAMPLE_ANNOTATIONS
    )

    a, b = 1, 2.0
    d = (3, 4.0)

    args, kwargs = replacer((a, b), {}, d)
    assert args == (3, 4.0)
    assert kwargs == {}

    args, kwargs = replacer((a,), dict(b=b), d)
    assert args == (3,)
    assert kwargs == dict(b=4.0)

    args, kwargs = replacer((), dict(a=a, b=b), d)
    assert args == ()
    assert kwargs == dict(a=3, b=4.0)

    args, kwargs = replacer((a, b, "c"), dict(), d)
    assert args == (3, 4.0, "c")
    assert kwargs == dict()

    args, kwargs = replacer((a, b), dict(c="c"), d)
    assert args == (3, 4.0)
    assert kwargs == dict(c="c")
