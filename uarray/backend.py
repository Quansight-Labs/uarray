from typing import Callable, Iterable, Dict, Tuple, Any, Set, Optional, Iterator
from abc import ABCMeta, abstractmethod
import inspect
from contextvars import ContextVar
import itertools

DispatcherType = Callable[..., Tuple]
ReverseDispatcherType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class MultiMethod:
    def __init__(self, dispatcher: DispatcherType, reverse_dispatcher: ReverseDispatcherType):
        self.dispatcher = dispatcher
        self.reverse_dispatcher = reverse_dispatcher
        self.__name__ = dispatcher.__name__
        self.__module__ = dispatcher.__module__
        self.__doc__ = dispatcher.__doc__
        self.__signature__ = inspect.signature(dispatcher)

    def __str__(self):
        return str(self.dispatcher)

    def __repr__(self):
        return repr(self.dispatcher)

    def __call__(self, *args, **kwargs):
        array_args = self.dispatcher(*args, **kwargs)

        for backend, coerce in _backend_order():
            if coerce:
                if self not in backend.methods:
                    raise RuntimeError('Method was not registered in the set backend while coercion was on.')

                array_args = tuple(backend.convertor(arr) for arr in array_args)
                args, kwargs = self.reverse_dispatcher(args, kwargs, array_args)
                result = backend.methods[self](self, args, kwargs)

                if result is NotImplemented:
                    raise RuntimeError('Method was not implemented in the set backend while coercion was on.')

                return result

            if self in backend.methods and backend.usable(array_args):
                result = backend.methods[self](self, args, kwargs)

                if result is not NotImplemented:
                    return result

        raise TypeError('No registered backends had an implementation for this method.')


def wrap_dispatcher(reverse_dispatcher: ReverseDispatcherType) -> Callable[[DispatcherType], MultiMethod]:
    def inner(dispatcher: DispatcherType) -> MultiMethod:
        return MultiMethod(dispatcher, reverse_dispatcher)

    return inner


ImplementationType = Callable[[MultiMethod, Iterable, Dict], Any]
MethodLookupType = Dict[MultiMethod, ImplementationType]
ConvertorType = Callable[[Any], Any]


class Backend(metaclass=ABCMeta):
    def __init__(self, convertor: ConvertorType = None):
        self._methods: MethodLookupType = {}
        self._convertor = convertor

    @property
    def methods(self):
        return self._methods

    @property
    def convertor(self):
        return self._convertor

    def register_method(self, method: MultiMethod, implementation: ImplementationType):
        self._methods[method] = implementation

    def deregister_method(self, method: MultiMethod):
        del self._methods[method]

    @abstractmethod
    def usable(self, array_args: Iterable) -> bool:
        pass


_backends: Set[Backend] = set()


def _backend_order() -> Iterator[Tuple[Backend, bool]]:
    pref = _preferred_backend.get()

    if pref is not None:
        yield (pref[0], bool(pref[1]))

    yield from itertools.product(_backends, (False,))

    if pref is not None and pref[1] is None:
        yield (pref[0], True)


class TypeCheckBackend(Backend):
    def __init__(self, types: Iterable[type], convertor: ConvertorType = None, allow_subclasses: bool = True):
        self.types = tuple(types)
        self.allow_subclasses = allow_subclasses
        super().__init__(convertor)

    def usable(self, array_args: Iterable) -> bool:
        if self.allow_subclasses:
            return all(isinstance(arr, self.types) for arr in array_args)
        else:
            return all(type(arr) in self.types for arr in array_args)


_preferred_backend: ContextVar[Optional[Tuple[Backend, Optional[bool]]]
                               ] = ContextVar('_preferred_backend', default=None)


class _SetBackend:
    def __init__(self, backend: Backend, coerce: Optional[bool] = None):
        self.token = _preferred_backend.set((backend, coerce))

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        _preferred_backend.reset(self.token)


set_backend = _SetBackend


def multimethod(backend: Backend, method: MultiMethod):
    def wrapper(func):
        def inner(method, args, kwargs):
            return func(*args, **kwargs)

        backend.register_method(method, inner)

        return func

    return wrapper


def register_backend(backend: Backend):
    _backends.add(backend)


def deregister_backend(backend: Backend):
    _backends.remove(backend)
