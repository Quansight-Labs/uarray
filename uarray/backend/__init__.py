from collections.abc import Hashable as _Hashable, Iterable as _Iterable
from abc import ABC as _ABC, abstractmethod as _abstractmethod
import contextvars as _contextvars

_backends = {}

_current_backend = _contextvars.ContextVar('_current_backend', default=None)

def __call__(key):
    return _backends[key]

class Backend(_ABC):
    @_abstractmethod
    def usable(self, arrays) -> bool:
        """
        Return a boolean representing whether this back-end is usable given the
        arrays or not.
        """

    def __enter__(self):
        self._token = _current_backend.set(self)
        return self

    def __exit__(self, type, value, traceback):
        _current_backend.reset(self._token)
        pass

    @property
    @_abstractmethod
    def bindings(self):
        """
        The bindings from given uarray methods to concrete implementations.
        """
    
    def register_binding(self, method, implementation):
        self.bindings[method] = implementation

class StrictTypeCheckBackend(Backend):
    def __init__(self, key, types):
        if not isinstance(key, _Hashable):
            raise ValueError("key should be hashable.")

        if not isinstance(types, _Iterable):
            types = (types,)

        if not all(isinstance(t, type) for t in types):
            raise ValueError("types must be a type or an iterable of types")

        self.key = key
        self.types = set(types)
        self._bindings = {}

    def usable(self, arrays):
        return all(type(arr) in self.types for arr in arrays)

    @property
    def bindings(self):
        return self._bindings

def register_backend(backend, types=None):
    if types is None:
        if not isinstance(backend, Backend):
            raise ValueError("If types is not supplied, backend must be of type uarray.backend.Backend")

        _backends[backend.key] = backend
    else:
        _backends[backend] = StrictTypeCheckBackend(backend, types)


class Method(object):
    def __init__(self, name, doc):
        self.__name__ = name
        self.__doc__ = doc

    def __str__(self):
        return f"uarray Method: {self.__name__}"

    __repr__ = __str__

    def __call__(self, arr_args, opts):
        current_backend = _current_backend.get()
        usable_backends = [current_backend] if current_backend is not None else \
            _backends.values()

        for backend in usable_backends:
            result = NotImplemented
            if backend.usable(arr_args) and self in backend.bindings:
                result = backend.bindings[self](arr_args, opts)

            if result is not NotImplemented:
                return result
        
        if current_backend is None:
            raise TypeError(f"No back-end had a matching implementation for {self.__name__}.")
        else:
            raise TypeError(f"Selected back-end had no matching implementation for {self.__name__}.")