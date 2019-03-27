from collections.abc import Iterable, Iterator

from uarray.backend import argument_extractor, Dispatchable


def _identity_argreplacer(args, kwargs, arrays):
    return args, kwargs


class UFunc(Dispatchable):
    @property  # type: ignore
    @argument_extractor(_identity_argreplacer)
    def nin(self):
        return ()

    @property  # type: ignore
    @argument_extractor(_identity_argreplacer)
    def nout(self):
        return ()

    @property  # type: ignore
    @argument_extractor(_identity_argreplacer)
    def types(self):
        return ()

    @property  # type: ignore
    @argument_extractor(_identity_argreplacer)
    def identity(self):
        return ()

    @property
    def nargs(self):
        return self.nin + self.nout

    @property
    def ntypes(self):
        return len(self.types)

    @staticmethod
    def _ufunc_argreplacer(args, kwargs, arrays):
        self = args[0]
        args = args[1:]
        in_args = arrays[:self.nin]
        out_args = arrays[self.nin:]

        out_args = in_args
        out_kwargs = {**kwargs, 'out': out_args}

        return out_args, out_kwargs

    @argument_extractor(_ufunc_argreplacer)
    def __call__(self, *args, out=None):
        in_args = tuple(args)
        if not isinstance(out, (Iterable, Iterator)):
            out_args = (out,)
        else:
            out_args = tuple(out)

        return in_args + out_args

    @staticmethod
    def _reduce_argreplacer(args, kwargs, arrays):
        out_args = list(args)
        out_args[1] = arrays[0]

        out_kwargs = {**kwargs, 'out': arrays[1]}

        return tuple(out_args), out_kwargs

    @argument_extractor(_reduce_argreplacer)
    def reduce(self, a, axis=0, dtype=None, out=None, keepdims=False):
        return (a, out)

    @argument_extractor(_reduce_argreplacer)
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

for ufunc_name in ufunc_list:
    globals()[ufunc_name] = UFunc()
