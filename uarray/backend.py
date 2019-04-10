from typing import Callable, Iterable, Dict, Tuple, Any, Set, Optional, Iterator, List, Type, Union
from abc import ABCMeta, abstractmethod
import inspect
from contextvars import ContextVar
import itertools
import functools

ArgumentExtractorType = Callable[..., Tuple["DispatchableInstance", ...]]
ArgumentReplacerType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class BackendNotImplementedError(TypeError):
    pass


class MultiMethod:
    def __init__(self, argument_extractor: ArgumentExtractorType, argument_replacer: ArgumentReplacerType,
                 default: Optional[Callable] = None):
        self.argument_extractor = argument_extractor
        self.argument_replacer = argument_replacer
        self.default = default
        self.__name__ = argument_extractor.__name__
        self.__module__ = argument_extractor.__module__
        self.__doc__ = argument_extractor.__doc__
        self.__signature__ = inspect.signature(argument_extractor)

    def __str__(self):
        return str(self.argument_extractor)

    def __repr__(self):
        return repr(self.argument_extractor)

    def __call__(self, *args, **kwargs):
        fallback_backends: List[Backend] = []

        for backend, coerce in _backend_order():
            current_args, current_kwargs, dispatchable_args = self.replace_dispatchables(
                backend, args, kwargs, coerce=coerce)
            usable = coerce or backend.usable(dispatchable_args)

            if usable is None or coerce is None:
                fallback_backends.append(backend)

            if not usable:
                continue

            result = self._try_backend(backend, current_args, current_kwargs)

            if result is NotImplemented:
                if coerce:
                    break
                continue

            return result

        for backend in fallback_backends:
            current_args, current_kwargs, dispatchable_args = self.replace_dispatchables(
                backend, args, kwargs, coerce=True)
            result = self._try_backend(backend, current_args, current_kwargs)

            if result is NotImplemented:
                continue

            return result

        raise BackendNotImplementedError('No selected backends had an implementation for this method.')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundMultiMethod(self, instance, owner)

    def _try_backend(self, backend: "Backend", args: Tuple, kwargs: Dict):
        result = NotImplemented

        if self in backend.dispatch_methods:
            result = backend.dispatch_methods[self](self, args, kwargs)

        if result is NotImplemented and self.default is not None:
            try:
                result = self.default(*args, **kwargs)
            except BackendNotImplementedError:
                pass

        if result is NotImplemented and None in backend.dispatch_methods:
            result = backend.dispatch_methods[None](self, args, kwargs)

        return result

    def replace_dispatchables(self, backend: "Backend", args, kwargs, coerce: Optional[bool] = False):
        dispatchable_args = self.argument_extractor(*args, **kwargs)
        replaced_args = tuple(self._replace_single(backend, arg, coerce=coerce) for arg in dispatchable_args)
        return (*self.argument_replacer(args, kwargs, replaced_args), dispatchable_args)

    def _replace_single(self, backend: "Backend", arg: Union["DispatchableInstance", Any],
                        coerce: Optional[bool] = False):
        if not isinstance(arg, DispatchableInstance):
            return arg

        arg_type = arg.dispatch_type

        if coerce:
            if arg.value is None:
                return None

            for try_type in arg_type.__mro__:
                if try_type in backend.convertors:
                    return backend.convertors[try_type](arg.value)

            raise BackendNotImplementedError('No selected backends had an implementation for this method.')

        return arg.value


class BoundMultiMethod:
    def __init__(self, method: MultiMethod, instance: Any, owner: Type):
        self.method = method
        self.instance = instance
        self.owner = owner

    def __call__(self, *args, **kwargs):
        return self.method.__call__(self.instance, *args, **kwargs)


def argument_extractor(reverse_dispatcher: ArgumentReplacerType,
                       default: Optional[Callable] = None) -> Callable[[ArgumentExtractorType], MultiMethod]:
    def inner(dispatcher: ArgumentExtractorType) -> MultiMethod:
        return MultiMethod(dispatcher, reverse_dispatcher, default=default)

    return inner


ImplementationType = Callable[[MultiMethod, Iterable, Dict], Any]
InstanceStubType = Any
ConvertorType = Callable[["DispatchableInstance"], Any]
MethodLookupType = Dict[Optional[MultiMethod], ImplementationType]
TypeLookupType = Dict[Type["DispatchableType"], ConvertorType]
InstanceLookupType = Dict["DispatchableInstance", InstanceStubType]


class Backend(metaclass=ABCMeta):
    def __init__(self):
        self._dispatch_methods: MethodLookupType = {}
        self._convertors: TypeLookupType = {}

    @property
    def dispatch_methods(self):
        return self._dispatch_methods

    @property
    def convertors(self):
        return self._convertors

    def register_method(self, method: MultiMethod, implementation: ImplementationType):
        self._dispatch_methods[method] = implementation

    def register_convertor(self, dispatch_type: Type["DispatchableType"], convertor: ConvertorType):
        self._convertors[dispatch_type] = convertor

    @abstractmethod
    def usable(self, dispatchable_args: Tuple["DispatchableInstance"]) -> Optional[bool]:
        pass


_backends: Set[Backend] = set()

BackendCoerceType = Tuple[Backend, Optional[bool]]


def _backend_order() -> Iterator[BackendCoerceType]:
    pref = _preferred_backend.get()
    skip = _skipped_backend.get()

    yield from filter(lambda x: x[0] not in skip, itertools.chain(pref, itertools.product(_backends, (False,))))


class TypeCheckBackend(Backend):
    def __init__(self, types: Iterable[type], allow_subclasses: bool = True,
                 fallback_types: Iterable[type] = (), allow_fallback_subclasses: Optional[bool] = None):
        self.types = tuple(types)
        self.allow_subclasses = allow_subclasses
        self.fallback_types = tuple((*fallback_types, *types))
        self.allow_fallback_subclasses = (allow_subclasses if allow_fallback_subclasses is None else
                                          allow_fallback_subclasses)
        super().__init__()

    def usable(self, dispatchable_args: Tuple["DispatchableInstance"]) -> Optional[bool]:
        args = tuple(map(lambda x: x.value if isinstance(x, DispatchableInstance) else x, dispatchable_args))

        if self.allow_subclasses:
            usable = all(isinstance(arr, self.types) for arr in args if arr is not None)
        else:
            usable = all(type(arr) in self.types for arr in args if arr is not None)

        if usable:
            return True

        if self.allow_fallback_subclasses:
            fallback = all(isinstance(arr, self.fallback_types)
                           for arr in args if arr is not None)
        else:
            fallback = all(type(arr) in self.fallback_types for arr in args if arr is not None)

        if fallback:
            return None

        return False


_preferred_backend: ContextVar[Tuple[BackendCoerceType, ...]] = ContextVar('_preferred_backend', default=())
_skipped_backend: ContextVar[Set[Backend]] = ContextVar('_skipped_backend', default=set())


class _SetBackend:
    def __init__(self, backend: Backend, coerce: Optional[bool] = None):
        self.token = _preferred_backend.set(((backend, coerce),) + _preferred_backend.get())

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        _preferred_backend.reset(self.token)


class _SkipBackend:
    def __init__(self, backend: Backend):
        new_skipped = set(_skipped_backend.get())
        new_skipped.add(backend)
        self.token = _skipped_backend.set(new_skipped)

    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, traceback):
        _skipped_backend.reset(self.token)


set_backend = _SetBackend
skip_backend = _SkipBackend


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


class DispatchableInstance:
    def __init__(self, dispatch_type: Union["DispatchableInstance", Type["DispatchableType"]],
                 value: Optional[Any] = None):
        if isinstance(dispatch_type, DispatchableInstance):
            self._type: Type[DispatchableType] = dispatch_type._type
            self._value = value
            return

        self._type: Type[DispatchableType] = dispatch_type
        self._value = value

    @property
    def dispatch_type(self):
        return self._type

    @property
    def value(self):
        return self._value


class DispatchableType:
    def __init__(self):
        if type(self) is DispatchableType:
            raise RuntimeError('Do not instantiate this class directly, '
                               'only through the metaclass DispatchableType.')


def all_of_type(arg_type: Type[DispatchableType]):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            extracted_args = func(*args, **kwargs)
            return tuple(DispatchableInstance(arg_type, arg) for arg in extracted_args)

        return inner

    return outer
