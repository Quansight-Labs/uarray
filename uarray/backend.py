from typing import Callable, Iterable, Dict, Tuple, Any, Set, Optional, Iterator, List, Type
from abc import ABCMeta, abstractmethod
import inspect
from contextvars import ContextVar
import itertools

ArgumentExtractorType = Callable[..., Tuple]
ArgumentReplacerType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class BackendNotImplementedError(TypeError):
    pass


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

        fallback_backends: List[Backend] = []

        for backend, coerce in _backend_order():
            if self.argument_extractor in backend.methods:
                usable = backend.usable(array_args)

                if usable is None or coerce is None:
                    fallback_backends.append(backend)

                if not usable and not coerce:
                    continue

                if coerce:
                    args, kwargs = self.replace_arrays(backend, args, kwargs)

                result = self._try_backend(backend, args, kwargs)

                if result is NotImplemented:
                    if coerce:
                        break
                    continue

                return result
            elif coerce:
                fallback_backends = []
                break

        for backend in fallback_backends:
            result = self._try_backend(backend, args, kwargs)

            if result is NotImplemented:
                continue

            return result

        raise BackendNotImplementedError('No selected backends had an implementation for this method.')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundMultiMethod(self, instance, owner)

    def _try_backend(self, backend, args, kwargs):
        return backend.methods[self.argument_extractor](self, args, kwargs)

    def replace_arrays(self, backend, args, kwargs):
        array_args = self.argument_extractor(*args, **kwargs)
        array_args = tuple(backend.convertor(arg) if arg is not None else arg
                           for arg in array_args)
        return self.argument_replacer(args, kwargs, array_args)


class BoundMultiMethod(MultiMethod):
    def __init__(self, method: MultiMethod, instance: Any, owner: Type):
        self.method = method
        self.instance = instance
        self.owner = owner
        argument_extractor = method.argument_extractor
        argument_replacer = method.argument_replacer

        super().__init__(argument_extractor, argument_replacer)

    def __call__(self, *args, **kwargs):
        return super().__call__(self.instance, *args, **kwargs)

    def _try_backend(self, backend, args, kwargs):
        if self.instance not in backend.instances:
            return super()._try_backend(backend, args, kwargs)

        backend_instance = backend.instances[self.instance]
        return super()._try_backend(backend, (backend_instance, *args[1:]), kwargs)


def argument_extractor(reverse_dispatcher: ArgumentReplacerType) -> Callable[[ArgumentExtractorType], MultiMethod]:
    def inner(dispatcher: ArgumentExtractorType) -> MultiMethod:
        return MultiMethod(dispatcher, reverse_dispatcher)

    return inner


ImplementationType = Callable[[MultiMethod, Iterable, Dict], Any]
MethodLookupType = Dict[ArgumentExtractorType, ImplementationType]
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
        self._methods[method.argument_extractor] = implementation

    def deregister_method(self, method: MultiMethod):
        del self._methods[method.argument_extractor]

    def register_instance(self, multiinstance: InstanceStubType, implementation: InstanceType):
        self._instances[multiinstance] = implementation

    @abstractmethod
    def usable(self, array_args: Iterable) -> Optional[bool]:
        pass


_backends: Set[Backend] = set()

BackendCoerceType = Tuple[Backend, Optional[bool]]


def _backend_order() -> Iterator[BackendCoerceType]:
    pref = _preferred_backend.get()

    yield from pref
    yield from itertools.product(_backends, (False,))


class TypeCheckBackend(Backend):
    def __init__(self, types: Iterable[type], convertor: ConvertorType = None, allow_subclasses: bool = True,
                 fallback_types: Iterable[type] = (), allow_fallback_subclasses: Optional[bool] = None):
        self.types = tuple(types)
        self.allow_subclasses = allow_subclasses
        self.fallback_types = tuple(fallback_types)
        self.allow_fallback_subclasses = (allow_subclasses if allow_fallback_subclasses is None else
                                          allow_fallback_subclasses)
        super().__init__(convertor)

    def usable(self, array_args: Iterable) -> Optional[bool]:
        if self.allow_subclasses:
            usable = all(isinstance(arr, self.types) for arr in array_args if arr is not None)
        else:
            usable = all(type(arr) in self.types for arr in array_args if arr is not None)

        if usable:
            return True

        if self.allow_fallback_subclasses:
            fallback = all(isinstance(arr, self.fallback_types) for arr in array_args if arr is not None)
        else:
            fallback = all(type(arr) in self.fallback_types for arr in array_args if arr is not None)

        if fallback:
            return None

        return False


_preferred_backend: ContextVar[Tuple[BackendCoerceType, ...]] = ContextVar('_preferred_backend', default=())


class _SetBackend:
    def __init__(self, backend: Backend, coerce: Optional[bool] = None):
        self.token = _preferred_backend.set(_preferred_backend.get() + ((backend, coerce),))

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


class Dispatchable(metaclass=ABCMeta):
    def __init__(self):
        if type(self) is Dispatchable:
            raise RuntimeError('Do not instantiate this class directly. '
                               'It is only meant to be inherited.')
