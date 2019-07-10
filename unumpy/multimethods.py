import functools
from uarray import create_multimethod, mark_as, all_of_type

create_numpy = functools.partial(create_multimethod, domain="numpy")


def _identity_argreplacer(args, kwargs, arrays):
    return args, kwargs


def _self_argreplacer(args, kwargs, dispatchables):
    def self_method(a, *args, **kwargs):
        return dispatchables + args, kwargs

    return self_method(*args, **kwargs)


def _ureduce_argreplacer(args, kwargs, dispatchables):
    def ureduce(self, a, axis=0, dtype=None, out=None, keepdims=False):
        return (
            (dispatchables[0], dispatchables[1]),
            dict(axis=axis, dtype=dtype, out=dispatchables[2], keepdims=keepdims),
        )

    return ureduce(*args, **kwargs)


def _reduce_argreplacer(args, kwargs, arrays):
    def reduce(a, axis=None, dtype=None, out=None, keepdims=False):
        kwargs = {}
        if dtype is not None:
            kwargs["dtype"] = dtype

        if keepdims is not False:
            kwargs["keepdims"] = keepdims

        return ((arrays[0],), dict(axis=axis, out=arrays[1], **kwargs))

    return reduce(*args, **kwargs)


def _first2argreplacer(args, kwargs, arrays):
    def func(a, b, **kwargs):
        return arrays, kwargs

    return func(*args, **kwargs)


class ndarray:
    pass


class ufunc:
    def __init__(self, name, nin, nout):
        self.name = name
        self.nin, self.nout = nin, nout

    def __str__(self):
        return "<ufunc '{}'>".format(self.name)

    @property  # type: ignore
    @create_numpy(_self_argreplacer)
    def types(self):
        return (mark_ufunc(self),)

    @property  # type: ignore
    @create_numpy(_self_argreplacer)
    def identity(self):
        return (mark_ufunc(self),)

    @property
    def nargs(self):
        return self.nin + self.nout

    @property
    def ntypes(self):
        return len(self.types)

    def _ufunc_argreplacer(args, kwargs, arrays):
        self = args[0]
        args = args[1:]
        in_arrays = arrays[1 : self.nin + 1]
        out_arrays = arrays[self.nin + 1 :]
        if self.nout == 1:
            out_arrays = out_arrays[0]

        if "out" in kwargs:
            kwargs = {**kwargs, "out": out_arrays}

        return (arrays[0], *in_arrays), kwargs

    @create_numpy(_ufunc_argreplacer)
    @all_of_type(ndarray)
    def __call__(self, *args, out=None):
        in_args = tuple(args)
        if not isinstance(out, tuple):
            out = (out,)

        return (mark_ufunc(self),) + in_args + out

    @create_numpy(_ureduce_argreplacer)
    @all_of_type(ndarray)
    def reduce(self, a, axis=0, dtype=None, out=None, keepdims=False):
        return (mark_ufunc(self), a, out)

    @create_numpy(_ureduce_argreplacer)
    @all_of_type(ndarray)
    def accumulate(self, a, axis=0, dtype=None, out=None):
        return (mark_ufunc(self), a, out)


mark_ufunc = mark_as(ufunc)


ufunc_list = [
    # Math operations
    "add",
    "subtract",
    "multiply",
    "divide",
    "logaddexp",
    "logaddexp2",
    "true_divide",
    "floor_divide",
    "negative",
    "positive",
    "power",
    "remainder",
    "mod",
    "fmod",
    "divmod",
    "absolute",
    "fabs",
    "rint",
    "sign",
    "heaviside",
    "conj",
    "exp",
    "exp2",
    "log",
    "log2",
    "log10",
    "expm1",
    "log1p",
    "sqrt",
    "square",
    "cbrt",
    "reciprocal",
    "gcd",
    "lcm",
    # Trigonometric functions
    "sin",
    "cos",
    "tan",
    "arcsin",
    "arccos",
    "arctan",
    "arctan2",
    "hypot",
    "sinh",
    "cosh",
    "tanh",
    "arcsinh",
    "arccosh",
    "arctanh",
    "deg2rad",
    "rad2deg",
    # Bit-twiddling functions
    "bitwise_and",
    "bitwise_or",
    "bitwise_xor",
    "invert",
    "left_shift",
    "right_shift",
    # Comparison functions
    "greater",
    "greater_equal",
    "less",
    "less_equal",
    "not_equal",
    "equal",
    "logical_and",
    "logical_or",
    "logical_xor",
    "logical_not",
    "maximum",
    "minimum",
    "fmax",
    "fmin",
    # Floating functions
    "isfinite",
    "isinf",
    "isnan",
    "isnat",
    "fabs",
    "signbit",
    "copysign",
    "nextafter",
    "spacing",
    "modf",
    "ldexp",
    "frexp",
    "fmod",
    "floor",
    "ceil",
    "trunc",
]

_args_mapper = {
    # Math operations
    "add": (2, 1),
    "subtract": (2, 1),
    "multiply": (2, 1),
    "divide": (2, 1),
    "logaddexp": (2, 1),
    "logaddexp2": (2, 1),
    "true_divide": (2, 1),
    "floor_divide": (2, 1),
    "negative": (1, 1),
    "positive": (1, 1),
    "power": (2, 1),
    "remainder": (2, 1),
    "mod": (2, 1),
    "fmod": (2, 1),
    "divmod": (2, 2),
    "absolute": (1, 1),
    "fabs": (1, 1),
    "rint": (1, 1),
    "sign": (1, 1),
    "heaviside": (1, 1),
    "conj": (1, 1),
    "exp": (1, 1),
    "exp2": (1, 1),
    "log": (1, 1),
    "log2": (1, 1),
    "log10": (1, 1),
    "expm1": (1, 1),
    "log1p": (1, 1),
    "sqrt": (1, 1),
    "square": (1, 1),
    "cbrt": (1, 1),
    "reciprocal": (1, 1),
    "gcd": (2, 1),
    "lcm": (2, 1),
    # Trigonometric functions
    "sin": (1, 1),
    "cos": (1, 1),
    "tan": (1, 1),
    "arcsin": (1, 1),
    "arccos": (1, 1),
    "arctan": (1, 1),
    "arctan2": (2, 1),
    "hypot": (2, 1),
    "sinh": (1, 1),
    "cosh": (1, 1),
    "tanh": (1, 1),
    "arcsinh": (1, 1),
    "arccosh": (1, 1),
    "arctanh": (1, 1),
    "deg2rad": (1, 1),
    "rad2deg": (1, 1),
    # Bit-twiddling functions
    "bitwise_and": (2, 1),
    "bitwise_or": (2, 1),
    "bitwise_xor": (2, 1),
    "invert": (1, 1),
    "left_shift": (2, 1),
    "right_shift": (2, 1),
    # Comparison functions
    "greater": (2, 1),
    "greater_equal": (2, 1),
    "less": (2, 1),
    "less_equal": (2, 1),
    "not_equal": (2, 1),
    "equal": (2, 1),
    "logical_and": (2, 1),
    "logical_or": (2, 1),
    "logical_xor": (2, 1),
    "logical_not": (1, 1),
    "maximum": (2, 1),
    "minimum": (2, 1),
    "fmax": (2, 1),
    "fmin": (2, 1),
    # Floating functions
    "isfinite": (1, 1),
    "isinf": (1, 1),
    "isnan": (1, 1),
    "isnat": (1, 1),
    "fabs": (1, 1),
    "signbit": (1, 1),
    "copysign": (2, 1),
    "nextafter": (2, 1),
    "spacing": (1, 1),
    "modf": (1, 2),
    "ldexp": (2, 1),
    "frexp": (1, 2),
    "fmod": (2, 1),
    "floor": (1, 1),
    "ceil": (1, 1),
    "trunc": (1, 1),
}

for ufunc_name in ufunc_list:
    globals()[ufunc_name] = ufunc(ufunc_name, *_args_mapper[ufunc_name])


@create_numpy(_identity_argreplacer)
def arange(start, stop=None, step=None, dtype=None):
    return ()


@create_numpy(_identity_argreplacer)
def array(object, dtype=None, copy=True, order="K", subok=False, ndmin=0):
    return ()


@create_numpy(_identity_argreplacer)
def zeros(shape, dtype=float, order="C"):
    return ()


@create_numpy(_identity_argreplacer)
def ones(shape, dtype=float, order="C"):
    return ()


@create_numpy(_identity_argreplacer)
def asarray(a, dtype=None, order=None):
    return ()


def reduce_impl(red_ufunc: ufunc):
    def inner(a, **kwargs):
        return red_ufunc.reduce(a, **kwargs)

    return inner


@create_numpy(_reduce_argreplacer, default=reduce_impl(globals()["add"]))
@all_of_type(ndarray)
def sum(a, axis=None, dtype=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer, default=reduce_impl(globals()["multiply"]))
@all_of_type(ndarray)
def prod(a, axis=None, dtype=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer, default=reduce_impl(globals()["minimum"]))
@all_of_type(ndarray)
def min(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer, default=reduce_impl(globals()["maximum"]))
@all_of_type(ndarray)
def max(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer, default=reduce_impl(globals()["logical_or"]))
@all_of_type(ndarray)
def any(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer, default=reduce_impl(globals()["logical_and"]))
@all_of_type(ndarray)
def all(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def argmin(a, axis=None, out=None):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def argmax(a, axis=None, out=None):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def nanmin(a, axis=None, out=None):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def nanmax(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def nansum(a, axis=None, dtype=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def nanprod(a, axis=None, dtype=None, out=None, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def std(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    return (a, out)


@create_numpy(_reduce_argreplacer)
@all_of_type(ndarray)
def var(a, axis=None, dtype=None, out=None, ddof=0, keepdims=False):
    return (a, out)


# set routines
@create_numpy(_self_argreplacer)
@all_of_type(ndarray)
def unique(a, return_index=False, return_inverse=False, return_counts=False, axis=None):
    return (a,)


@create_numpy(_first2argreplacer)
@all_of_type(ndarray)
def in1d(element, test_elements, assume_unique=False, invert=False):
    return (element, test_elements)


def _isin_default(element, test_elements, assume_unique=False, invert=False):
    return in1d(
        element, test_elements, assume_unique=assume_unique, invert=invert
    ).reshape(element.shape)


@create_numpy(_first2argreplacer, default=_isin_default)
@all_of_type(ndarray)
def isin(element, test_elements, assume_unique=False, invert=False):
    return (element, test_elements)


@create_numpy(_first2argreplacer)
@all_of_type(ndarray)
def intersect1d(ar1, ar2, assume_unique=False, return_indices=False):
    return (ar1, ar2)


def _setdiff1d_default(ar1, ar2, assume_unique=False):
    if assume_unique:
        ar1 = asarray(ar1).ravel()
    else:
        ar1 = unique(ar1)
        ar2 = unique(ar2)
    return ar1[in1d(ar1, ar2, assume_unique=True, invert=True)]


@create_numpy(_first2argreplacer, default=_setdiff1d_default)
@all_of_type(ndarray)
def setdiff1d(ar1, ar2, assume_unique=False):
    return (ar1, ar2)


@create_numpy(_first2argreplacer)
@all_of_type(ndarray)
def setxor1d(ar1, ar2, assume_unique=False):
    return (ar1, ar2)


@create_numpy(_first2argreplacer)
@all_of_type(ndarray)
def union1d(ar1, ar2):
    return (ar1, ar2)


@create_numpy(_self_argreplacer)
@all_of_type(ndarray)
def sort(a, axis=None, kind=None, order=None):
    return (a,)


def _tuple_check_argreplacer(args, kwargs, arrays):
    if len(arrays) == 1:
        return arrays + args[1:], kwargs
    else:
        return (arrays,) + args[1:], kwargs


@create_numpy(_tuple_check_argreplacer)
@all_of_type(ndarray)
def lexsort(keys, axis=None):
    if isinstance(keys, tuple):
        return keys
    else:
        return (keys,)


def _args_argreplacer(args, kwargs, arrays):
    return arrays, kwargs


@create_numpy(_args_argreplacer)
@all_of_type(ndarray)
def broadcast_arrays(*args, subok=False):
    return args


@create_numpy(_self_argreplacer)
@all_of_type(ndarray)
def broadcast_to(array, shape, subok=False):
    return (array,)


def _first_argreplacer(args, kwargs, arrays1):
    def func(arrays, axis=0, out=None):
        return (arrays1,), dict(axis=0, out=None)

    return func(*args, **kwargs)


@create_numpy(_first_argreplacer)
@all_of_type(ndarray)
def concatenate(arrays, axis=0, out=None):
    return arrays


@create_numpy(_first_argreplacer)
@all_of_type(ndarray)
def stack(arrays, axis=0, out=None):
    return arrays


@create_numpy(_self_argreplacer)
@all_of_type(ndarray)
def argsort(a, axis=-1, kind="quicksort", order=None):
    return (a,)


@create_numpy(_self_argreplacer, default=lambda a: sort(a, axis=0))
@all_of_type(ndarray)
def msort(a):
    return (a,)


@create_numpy(_self_argreplacer, default=lambda a: sort(a))
@all_of_type(ndarray)
def sort_complex(a):
    return (a,)


@create_numpy(_self_argreplacer)
@all_of_type(ndarray)
def partition(a, kth, axis=-1, kind="introselect", order=None):
    return (a,)


@create_numpy(_self_argreplacer)
@all_of_type(ndarray)
def argpartition(a, kth, axis=-1, kind="introselect", order=None):
    return (a,)


del ufunc_name
