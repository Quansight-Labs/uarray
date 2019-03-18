from typing import Callable, Iterable, Dict, Tuple, Any, Set
from abc import ABCMeta, abstractmethod

DispatcherType = Callable[..., Iterable]
ReverseDispatcherType = Callable[[Iterable, Dict, Iterable], Tuple[Iterable, Dict]]


class Method:
    def __init__(self, dispatcher: DispatcherType, reverse_dispatcher: ReverseDispatcherType):
        self.dispatcher = dispatcher
        self.reverse_dispatcher = reverse_dispatcher
        self.__name__ = dispatcher.__name__
        self.__module__ = dispatcher.__module__
        self.__doc__ = dispatcher.__doc__

    def __str__(self):
        return str(self.dispatcher)

    def __repr__(self):
        return repr(self.dispatcher)

    def __call__(self, *args, **kwargs):
        array_args = self.dispatcher(*args, **kwargs)

        for backend in _backends:
            if self in backend.methods and backend.usable(array_args):
                result = backend.methods[self](self, args, kwargs)

                if result is not NotImplemented:
                    return result

        raise TypeError('No registered backends had an implementation for this method.')


def wrap_dispatcher(reverse_dispatcher: ReverseDispatcherType) -> Callable[[DispatcherType], Method]:
    def inner(dispatcher: DispatcherType) -> Method:
        return Method(dispatcher, reverse_dispatcher)

    return inner


ImplementationType = Callable[[Method, Iterable, Dict], Any]
MethodLookupType = Dict[Method, ImplementationType]
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

    def register_method(self, method: Method, implementation: ImplementationType):
        self._methods[method] = implementation

    def deregister_method(self, method: Method):
        del self._methods[method]

    @abstractmethod
    def usable(self, array_args: Iterable) -> bool:
        pass


_backends: Set[Backend] = set()


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


def register_backend(backend: Backend):
    _backends.add(backend)


def deregister_backend(backend: Backend):
    _backends.remove(backend)
