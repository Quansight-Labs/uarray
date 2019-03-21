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
        out_kwargs = {'out': out_args}

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
        return tuple(out_args), kwargs

    @argument_extractor(_reduce_argreplacer)
    def reduce(self, a, axis=0, dtype=None, out=None, keepdims=False):
        return (a, out)


add = UFunc()
