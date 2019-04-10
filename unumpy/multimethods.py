from uarray.backend import create_multimethod, DispatchableInstance, all_of_type


def _identity_argreplacer(args, kwargs, arrays):
    return args, kwargs


def _ureduce_argreplacer(args, kwargs, arrays):
    out_args = list(args)
    out_args[1] = arrays[0]

    out_kwargs = {**kwargs, 'out': arrays[1]}

    return tuple(out_args), out_kwargs


def _reduce_argreplacer(args, kwargs, arrays):
    out_args = list(args)
    out_args[0] = arrays[0]

    out_kwargs = {**kwargs, 'out': arrays[1]}

    return tuple(out_args), out_kwargs


class ndarray(DispatchableInstance):
    pass


class ufunc(DispatchableInstance):
    def __init__(self, name, nin, nout):
        self.name = name
        self._nin = nin
        self._nout = nout
        super().__init__(self)

    def __str__(self):
        return f"<ufunc '{self.name}'>"

    @property
    def nin(self):
        return self._nin

    @property
    def nout(self):
        return self._nout

    @property  # type: ignore
    @create_multimethod(_identity_argreplacer)
    def types(self):
        return ()

    @property  # type: ignore
    @create_multimethod(_identity_argreplacer)
    def identity(self):
        return ()

    @property
    def nargs(self):
        return self.nin + self.nout

    @property
    def ntypes(self):
        return len(self.types)

    def _ufunc_argreplacer(args, kwargs, arrays):
        self = args[0]
        args = args[1:]
        in_arrays = arrays[:self.nin]
        out_arrays = arrays[self.nin:]
        if self.nout == 1:
            out_arrays = out_arrays[0]
        out_kwargs = {**kwargs, 'out': out_arrays}

        return (self, *in_arrays), out_kwargs

    @create_multimethod(_ufunc_argreplacer)
    @all_of_type(ndarray)
    def __call__(self, *args, out=None):
        in_args = tuple(args)
        if not isinstance(out, tuple):
            out = (out,)

        return in_args + out

    @create_multimethod(_ureduce_argreplacer)
    @all_of_type(ndarray)
    def reduce(self, a, axis=0, dtype=None, out=None, keepdims=False):
        return (a, out)

    @create_multimethod(_ureduce_argreplacer)
    @all_of_type(ndarray)
    def accumulate(self, a, axis=0, dtype=None, out=None):
        return (a, out)


ufunc_list = [
    # Math operations
    'add', 'subtract', 'multiply', 'divide', 'logaddexp', 'logaddexp2',
    'true_divide', 'floor_divide', 'negative', 'positive', 'power',
    'remainder', 'mod', 'fmod', 'divmod', 'absolute', 'fabs', 'rint',
    'sign', 'heaviside', 'conj', 'exp', 'exp2', 'log', 'log2', 'log10',
    'expm1', 'log1p', 'sqrt', 'square', 'cbrt', 'reciprocal', 'gcd',
    'lcm',

    # Trigonometric functions
    'sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan', 'arctan2',
    'hypot', 'sinh', 'cosh', 'tanh', 'arcsinh', 'arccosh',
    'arctanh', 'deg2rad', 'rad2deg',

    # Bit-twiddling functions
    'bitwise_and', 'bitwise_or', 'bitwise_xor', 'invert', 'left_shift',
    'right_shift',

    # Comparison functions
    'greater', 'greater_equal', 'less', 'less_equal', 'not_equal',
    'equal', 'logical_and', 'logical_or', 'logical_xor', 'logical_not',
    'maximum', 'minimum', 'fmax', 'fmin',

    # Floating functions
    'isfinite', 'isinf', 'isnan', 'isnat', 'fabs', 'signbit', 'copysign',
    'nextafter', 'spacing', 'modf', 'ldexp', 'frexp', 'fmod', 'floor',
    'ceil', 'trunc'
]

_args_mapper = {
    # Math operations
    'add': (2, 1),
    'subtract': (2, 1),
    'multiply': (2, 1),
    'divide': (2, 1),
    'logaddexp': (2, 1),
    'logaddexp2': (2, 1),
    'true_divide': (2, 1),
    'floor_divide': (2, 1),
    'negative': (1, 1),
    'positive': (1, 1),
    'power': (2, 1),
    'remainder': (2, 1),
    'mod': (2, 1),
    'fmod': (2, 1),
    'divmod': (2, 2),
    'absolute': (1, 1),
    'fabs': (1, 1),
    'rint': (1, 1),
    'sign': (1, 1),
    'heaviside': (1, 1),
    'conj': (1, 1),
    'exp': (1, 1),
    'exp2': (1, 1),
    'log': (1, 1),
    'log2': (1, 1),
    'log10': (1, 1),
    'expm1': (1, 1),
    'log1p': (1, 1),
    'sqrt': (1, 1),
    'square': (1, 1),
    'cbrt': (1, 1),
    'reciprocal': (1, 1),
    'gcd': (2, 1),
    'lcm': (2, 1),

    # Trigonometric functions
    'sin': (1, 1),
    'cos': (1, 1),
    'tan': (1, 1),
    'arcsin': (1, 1),
    'arccos': (1, 1),
    'arctan': (1, 1),
    'arctan2': (2, 1),
    'hypot': (2, 1),
    'sinh': (1, 1),
    'cosh': (1, 1),
    'tanh': (1, 1),
    'arcsinh': (1, 1),
    'arccosh': (1, 1),
    'arctanh': (1, 1),
    'deg2rad': (1, 1),
    'rad2deg': (1, 1),

    # Bit-twiddling functions
    'bitwise_and': (2, 1),
    'bitwise_or': (2, 1),
    'bitwise_xor': (2, 1),
    'invert': (1, 1),
    'left_shift': (2, 1),
    'right_shift': (2, 1),

    # Comparison functions
    'greater': (2, 1),
    'greater_equal': (2, 1),
    'less': (2, 1),
    'less_equal': (2, 1),
    'not_equal': (2, 1),
    'equal': (2, 1),
    'logical_and': (2, 1),
    'logical_or': (2, 1),
    'logical_xor': (2, 1),
    'logical_not': (1, 1),
    'maximum': (2, 1),
    'minimum': (2, 1),
    'fmax': (2, 1),
    'fmin': (2, 1),

    # Floating functions
    'isfinite': (1, 1),
    'isinf': (1, 1),
    'isnan': (1, 1),
    'isnat': (1, 1),
    'fabs': (1, 1),
    'signbit': (1, 1),
    'copysign': (2, 1),
    'nextafter': (2, 1),
    'spacing': (1, 1),
    'modf': (1, 2),
    'ldexp': (2, 1),
    'frexp': (1, 2),
    'fmod': (2, 1),
    'floor': (1, 1),
    'ceil': (1, 1),
    'trunc': (1, 1),
}

for ufunc_name in ufunc_list:
    globals()[ufunc_name] = ufunc(ufunc_name, *_args_mapper[ufunc_name])


@create_multimethod(_identity_argreplacer)
def arange(start, stop, step, dtype=None):
    return ()


@create_multimethod(_identity_argreplacer)
def array(object, dtype=None, copy=True, order='K', subok=False, ndmin=0):
    return ()


@create_multimethod(_identity_argreplacer)
def zeros(shape, dtype=float, order='C'):
    return ()


@create_multimethod(_identity_argreplacer)
def ones(shape, dtype=float, order='C'):
    return ()


@create_multimethod(_identity_argreplacer)
def asarray(a, dtype=None, order=None):
    return ()


def reduce_impl(red_ufunc: ufunc):
    def inner(a, **kwargs):
        return red_ufunc.reduce(a, **kwargs)

    return inner


@create_multimethod(_reduce_argreplacer, default=reduce_impl(globals()['add']))
def sum(a, axis=None, dtype=None, out=None, keepdims=False):
    return (a, out)


@create_multimethod(_reduce_argreplacer, default=reduce_impl(globals()['multiply']))
def prod(a, axis=None, dtype=None, out=None, keepdims=False):
    return (a, out)


@create_multimethod(_reduce_argreplacer, default=reduce_impl(globals()['minimum']))
def min(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_multimethod(_reduce_argreplacer, default=reduce_impl(globals()['maximum']))
def max(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_multimethod(_reduce_argreplacer, default=reduce_impl(globals()['logical_or']))
def any(a, axis=None, out=None, keepdims=False):
    return (a, out)


@create_multimethod(_reduce_argreplacer, default=reduce_impl(globals()['logical_and']))
def all(a, axis=None, out=None, keepdims=False):
    return (a, out)


del ufunc_name
