from typing import Callable, Iterable, Dict, Tuple, Any, Set, Optional, Iterator
from abc import ABCMeta, abstractmethod
import inspect
from contextvars import ContextVar
import itertools
import functools

ArgumentExtractorType = Callable[..., Tuple]
ArgumentReplacerType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class MultiMethod:
    def __init__(self, argument_extractor: ArgumentExtractorType, argument_replacer: ArgumentReplacerType):
        self.argument_extractor = argument_extractor
        self.argument_replacer = argument_replacer
        self.__name__ = argument_extractor.__name__
        self.__module__ = argument_extractor.__module__
        self.__doc__ = argument_extractor.__doc__
        self.__signature__ = inspect.signature(argument_extractor)

    def __str__(self):
        return str(self.argument_extractor)

    def __repr__(self):
        return repr(self.argument_extractor)

    def __call__(self, *args, **kwargs):
        array_args = self.argument_extractor(*args, **kwargs)

        for backend, coerce in _backend_order():
            if coerce:
                if self not in backend.methods:
                    break

                array_args = tuple(backend.convertor(arr) for arr in array_args)
                args, kwargs = self.argument_replacer(args, kwargs, array_args)
                result = backend.methods[self](self, args, kwargs)

                if result is NotImplemented:
                    break

                return result

            if self in backend.methods and backend.usable(array_args):
                result = backend.methods[self](self, args, kwargs)

                if result is not NotImplemented:
                    return result

        raise TypeError('No selected backends had an implementation for this method.')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self.__call__, instance)


def argument_extractor(reverse_dispatcher: ArgumentReplacerType) -> Callable[[ArgumentExtractorType], MultiMethod]:
    def inner(dispatcher: ArgumentExtractorType) -> MultiMethod:
        return MultiMethod(dispatcher, reverse_dispatcher)

    return inner


ImplementationType = Callable[[MultiMethod, Iterable, Dict], Any]
MethodLookupType = Dict[MultiMethod, ImplementationType]
InstanceType = Any
InstanceStubType = Any
InstanceLookupType = Dict[InstanceStubType, InstanceType]
ConvertorType = Callable[[Any], Any]


class Backend(metaclass=ABCMeta):
    def __init__(self, convertor: ConvertorType = None):
        self._methods: MethodLookupType = {}
        self._instances: InstanceLookupType = {}
        self._convertor = convertor

    @property
    def methods(self):
        return self._methods

    @property
    def instances(self):
        return self._instances

    @property
    def convertor(self):
        return self._convertor

    def register_method(self, method: MultiMethod, implementation: ImplementationType):
        self._methods[method] = implementation

    def deregister_method(self, method: MultiMethod):
        del self._methods[method]

    def register_instance(self, cls: InstanceStubType, implementation: InstanceType):
        self._instances[cls] = implementation

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
            return all(isinstance(arr, self.types) for arr in array_args if arr is not None)
        else:
            return all(type(arr) in self.types for arr in array_args if arr is not None)


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


def instance_multimethod(backend: Backend, method: MultiMethod):
    def wrapper(func):
        def inner(method, args, kwargs):
            return func(backend.instances[args[0]], *args[1:], **kwargs)

        backend.register_method(method, inner)

        return func

    return wrapper


def register_backend(backend: Backend):
    _backends.add(backend)


def deregister_backend(backend: Backend):
    _backends.remove(backend)


class Dispatchable(metaclass=ABCMeta):
    def __init__(self):
        if type(self) is Dispatchable:
            raise RuntimeError('Do not instantiate this class directly. '
                               'It is only meant to be inherited.')
