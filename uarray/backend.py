from typing import Callable, Iterable, Dict, Tuple, Any, Set, Optional, Iterator, List, Type, Union
from abc import ABCMeta, abstractmethod
import inspect
from contextvars import ContextVar
import itertools
import functools

ArgumentExtractorType = Callable[..., Tuple["DispatchableInstance", ...]]
ArgumentReplacerType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class BackendNotImplementedError(NotImplementedError):
    """
    An exception that is thrown when no compatible backend is found for a method.
    """


class MultiMethod:
    """
    This class is meant to provide a dispatchable method with or without a registered implementation.

    Provides a multi-method instance. The method has no implementation by default, but one can be provided
    if needed. :obj:`Backend` s can provide implementations for the method, and users can choose backends.

    Parameters
    ----------
    argument_extractor : ArgumentExtractorType
        This is a callable that extracts the arguments using which dispatch can be performed from this
        multimethod.
    argument_replacer : ArgumentReplacerType
        This takes in args, kwargs and dispatchable args, and replaces all dispatchable arguments within
        the args and kwargs, and then returns them.
    default : Optional[Callable]
        This is the default implementation for this multimethod, possibly in terms of other multimethods.

    Examples
    --------
    >>> import uarray as ua
    >>> def potato(a, b):
    ...     return (a,) # b is not is dispatchable, so we return a only
    >>> def potato_rd(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs
    >>> def potato_impl(a, b):
    ...     # The default implementation passes through all arguments
    ...     return a, b
    >>> potato_mm = ua.MultiMethod(potato, potato_rd, default=potato_impl)
    >>> potato_mm(1, '2')
    (1, '2')
    >>> be = ua.TypeCheckBackend((int,)) # Register implementation, define "supported dispatchable types"
    >>> @ua.register_implementation(be, potato_mm)
    ... def potato_impl_be(a, b):
    ...     return 'potato'
    >>> with ua.set_backend(be):
    ...     potato_mm(1, '2')
    'potato'
    >>> potato_mm(1, '2')
    (1, '2')
    >>> be2 = ua.TypeCheckBackend(())
    >>> potato_mm2 = ua.MultiMethod(potato, potato_rd)
    >>> with ua.set_backend(be2):
    ...     potato_mm2(1, '2')
    Traceback (most recent call last):
        ...
    uarray.backend.BackendNotImplementedError: No selected backends had an implementation for this method.
    """

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
            current_args, current_kwargs, dispatchable_args = backend.replace_dispatchables(
                self, args, kwargs, coerce=coerce)
            usable = coerce or backend.usable(dispatchable_args)

            if usable is None or coerce is None:
                fallback_backends.append(backend)

            if not usable:
                continue

            result = backend.try_backend(self, current_args, current_kwargs)

            if result is NotImplemented:
                if coerce:
                    break
                continue

            return result

        for backend in fallback_backends:
            current_args, current_kwargs, dispatchable_args = backend.replace_dispatchables(
                self, args, kwargs, coerce=True)
            result = backend.try_backend(self, current_args, current_kwargs)

            if result is NotImplemented:
                continue

            return result

        raise BackendNotImplementedError('No selected backends had an implementation for this method.')

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundMultiMethod(self, instance, owner)


class BoundMultiMethod:
    """
    Used internally for the implementation of the descriptor protocol.
    """
    def __init__(self, method: Union[MultiMethod, "BoundMultiMethod"], instance: Any, owner: Type):
        self.method = method
        self.instance = instance
        self.owner = owner

    def __call__(self, *args, **kwargs):
        return self.method.__call__(self.instance, *args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundMultiMethod(self, instance, owner)


def create_multimethod(reverse_dispatcher: ArgumentReplacerType,
                       default: Optional[Callable] = None) -> Callable[[ArgumentExtractorType], MultiMethod]:
    """
    Returns a decorator that can be used to create a :obj:`MultiMethod` from an argument extractor.

    Parameters
    ----------
    argument_replacer : ArgumentReplacerType
        This takes in args, kwargs and dispatchable args, and replaces all dispatchable arguments within
        the args and kwargs, and then returns them.
    default : Optional[Callable]
        This is the default implementation for this multimethod, possibly in terms of other multimethods.

    Examples
    --------
    This example shows how a :obj:`MultiMethod` can be created in a functional manner from an argument
    extractor. The following will create an equivalent :obj:`MultiMethod` to that in its documentation.

    >>> import uarray as ua
    >>> def potato_rd(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs
    >>> def potato_impl(a, b):
    ...     # The default implementation passes through all arguments
    ...     return a, b
    >>> @ua.create_multimethod(potato_rd, default=potato_impl)
    ... def potato(a, b):
    ...     return (a,)
    """
    def inner(dispatcher: ArgumentExtractorType) -> MultiMethod:
        return MultiMethod(dispatcher, reverse_dispatcher, default=default)

    return inner


ImplementationType = Callable[[MultiMethod, Iterable, Dict], Any]
InstanceStubType = Any
ConvertorType = Callable[["DispatchableInstance"], Any]
MethodLookupType = Dict[Optional[MultiMethod], ImplementationType]
TypeLookupType = Dict[Type["DispatchableInstance"], ConvertorType]
InstanceLookupType = Dict["DispatchableInstance", InstanceStubType]


class Backend(metaclass=ABCMeta):
    """
    An abstract base class for all backend types.
    """
    def __init__(self):
        self._implementations: MethodLookupType = {}
        self._convertors: TypeLookupType = {}

    def register_implementation(self, method: MultiMethod, implementation: ImplementationType):
        """
        Register this backend's implementation for a given method.

        Parameters
        ----------
        method : MultiMethod
            The method to register the implementation for.
        implementation: ImplementationType
            The implementation of this method. It takes in (method, args, kwargs) and returns
            either a result or ``NotImplemented``. Any exceptions (except :obj:`BackendNotImplementedError`)
            will be propagated.

        Examples
        --------
        >>> import uarray as ua
        >>> def potato_rd(args, kwargs, dispatch_args):
        ...     # This replaces a within the args/kwargs
        ...     return dispatch_args + args[1:], kwargs
        >>> @ua.create_multimethod(potato_rd)
        ... def potato(a, b):
        ...     return (a,) # a, b is not is dispatchable, so we return a only
        >>> be = ua.TypeCheckBackend((int,))  # Define "supported dispatchable types"
        >>> def potato_impl(method, args, kwargs):
        ...     # method will be potato
        ...     return args, kwargs
        >>> be.register_implementation(potato, potato_impl)
        >>> with ua.set_backend(be):
        ...     potato(1, '2')
        ((1, '2'), {})
        >>> be.register_implementation(potato, potato_impl)
        Traceback (most recent call last):
            ...
        ValueError: Cannot register a different method once one is already registered.

        Raises
        ------
        ValueError
            If an implementation has already been registered for the given method.
        """
        if method in self._implementations:
            raise ValueError('Cannot register a different method once one is already registered.')

        self._implementations[method] = implementation

    def register_convertor(self, dispatch_type: Type["DispatchableInstance"], convertor: ConvertorType):
        """
        Registers a convertor for a given type.

        The convertor takes in a single value and converts it to a form suitable for consumption by
        the backend's implementations. It's called when the user coerces the type and the backend
        has also registered the type of the dispatchable.

        Parameters
        ----------
        dispatch_type : Type["DispatchableInstance"]
            The type of dispatchable to register the convertor for. The convertor will convert the
            instance if coercion is enabled.
        implementation: ImplementationType
            The implementation of this method. It takes in a single value and converts it.

        Raises
        ------
        ValueError
            If there is already a convertor for this type.

        Examples
        --------
        >>> import uarray as ua
        >>> class DispatchableInt(ua.DispatchableInstance):
        ...     pass
        >>> be = ua.TypeCheckBackend((int,))
        >>> # All ints piped to -2
        >>> be.register_convertor(DispatchableInt, lambda x: -2)
        >>> def potato_rd(args, kwargs, dispatch_args):
        ...     # This replaces a within the args/kwargs
        ...     return dispatch_args + args[1:], kwargs
        >>> @ua.create_multimethod(potato_rd)
        ... def potato(a, b):
        ...     # Here, we register a as dispatchable and mark it as an int
        ...     return (DispatchableInt(a),)
        >>> @ua.register_implementation(be, potato)
        ... def potato_impl(a, b):
        ...     return a, b
        >>> with ua.set_backend(be, coerce=True):
        ...     potato(1, '2')
        (-2, '2')
        >>> be.register_convertor(DispatchableInt, lambda x: -2)
        Traceback (most recent call last):
            ...
        ValueError: Cannot register a different convertor once one is already registered.
        """
        if dispatch_type in self._convertors:
            raise ValueError('Cannot register a different convertor once one is already registered.')

        self._convertors[dispatch_type] = convertor

    @abstractmethod
    def usable(self, dispatchable_args: Tuple["DispatchableInstance"]) -> Optional[bool]:
        """
        An abstract property that, given the dispatchable args, returns either a boolean
        indicating whether the backend can be used, or ``None`` if it should be used as
        a fallback.
        """
        pass

    def replace_dispatchables(self, method: MultiMethod, args, kwargs, coerce: Optional[bool] = False):
        """
        Replace dispatchables for a this method, using the convertor, if coercion is used.

        Parameters
        ----------
        method : MultiMethod
            The method to replace the args/kwargs for.
        args, kwargs
            The args and kwargs to replace.
        coerce: Optional[bool]
            Whether or not to coerce the arrays during replacement. Default is False.
        """
        dispatchable_args = method.argument_extractor(*args, **kwargs)
        replaced_args = tuple(self._replace_single(arg, coerce=coerce) for arg in dispatchable_args)
        return (*method.argument_replacer(args, kwargs, replaced_args), replaced_args)

    def _replace_single(self, arg: Union["DispatchableInstance", Any],
                        coerce: Optional[bool] = False):
        if not isinstance(arg, DispatchableInstance):
            return arg

        arg_type = type(arg)

        if coerce:
            if arg.value is None:
                return None

            for try_type in arg_type.__mro__:
                if try_type in self._convertors:
                    return self._convertors[try_type](arg.value)

        return arg.value

    def try_backend(self, method: MultiMethod, args: Tuple, kwargs: Dict):
        """
        Try this backend for a given args and kwargs. Returns either a
        result or ``NotImplemented``. All exceptions are propagated.
        """
        result = NotImplemented

        if method in self._implementations:
            result = self._implementations[method](method, args, kwargs)

        if result is NotImplemented and method.default is not None:
            try:
                result = method.default(*args, **kwargs)
            except BackendNotImplementedError:
                pass

        if result is NotImplemented and None in self._implementations:
            result = self._implementations[None](method, args, kwargs)

        return result


_backends: Set[Backend] = set()

BackendCoerceType = Tuple[Backend, Optional[bool]]


def _backend_order() -> Iterator[BackendCoerceType]:
    pref = _preferred_backend.get()
    skip = _skipped_backend.get()

    yield from filter(lambda x: x[0] not in skip, itertools.chain(pref, itertools.product(_backends, (False,))))


class TypeCheckBackend(Backend):
    """
    A backend that's based on type-checking based dispatch.

    Parameters
    ----------
    types : Iterable[Type]
        The types this backend supports.
    allow_subclasses: bool, optional
        Whether to allow subclasses when checking the types. Default is ``True``.
    fallback_types: Iterable[Type], optional
        The types for which this backend is a fallback.
    allow_fallback_subclasses: Optional[bool], optional
        Whether to allow subclasses for fallback types. Default is ``None``, which means
        "use whatever value ``allow_subclasses`` has."
    """
    def __init__(self, types: Iterable[Type], allow_subclasses: bool = True,
                 fallback_types: Iterable[Type] = (), allow_fallback_subclasses: Optional[bool] = None):
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


class set_backend:
    """
    A context manager that sets the preferred backend.

    Parameters
    ----------
    backend : Backend
        The backend to set.
    coerce: Optional[bool], optional
        Whether to coerce the input arguments, where ``None`` lets this
        backend be used as a fallback with coercion on failure.

    See Also
    --------
    skip_backend: A context manager that allows skipping of backends.
    """
    def __init__(self, backend: Backend, coerce: Optional[bool] = None):
        self.token = None
        self.backend = backend
        self.coerce = coerce

    def __enter__(self):
        self.token = _preferred_backend.set(((self.backend, self.coerce),) + _preferred_backend.get())

    def __exit__(self, exception_type, exception_value, traceback):
        _preferred_backend.reset(self.token)


class skip_backend:
    """
    Provides the ability to skip the preferred backend in a thread-safe manner.

    When combined with :obj:`set_backend`, this context manager takes precedence.

    Parameters
    ----------
    backend : Backend
        The backend to skip.

    See Also
    --------
    set_backend: A context manager that allows setting of preferred backend.
    """
    def __init__(self, backend: Backend):
        self.backend = backend
        self.token = None

    def __enter__(self):
        new_skipped = set(_skipped_backend.get())
        new_skipped.add(self.backend)
        self.token = _skipped_backend.set(new_skipped)

    def __exit__(self, exception_type, exception_value, traceback):
        _skipped_backend.reset(self.token)


def register_implementation(backend: Backend, method: MultiMethod):
    """
    Create an implementation for a given backend/method. The implementation
    should have the same signature as the method, or perhaps with some optional
    keyword arguments missing.
    """
    def wrapper(func):
        @functools.wraps(func)
        def inner(method, args, kwargs):
            return func(*args, **kwargs)

        backend.register_implementation(method, inner)

        return func

    return wrapper


def register_backend(backend: Backend):
    _backends.add(backend)


def deregister_backend(backend: Backend):
    _backends.remove(backend)


class DispatchableInstance:
    """
    A marker class. This class is meant to be inherited from so that dispatchable arguments
    can be marked by their "dispatch type".

    Parameters
    ----------
    value
        The value of the DispatchableInstance.

    Examples
    --------
    >>> import uarray as ua
    >>> class DispatchableInt(ua.DispatchableInstance):
    ...     pass
    >>> be = ua.TypeCheckBackend((int,))
    >>> # All ints piped to -2
    >>> be.register_convertor(DispatchableInt, lambda x: -2)
    >>> def potato_rd(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs
    >>> @ua.create_multimethod(potato_rd)
    ... def potato(a, b):
    ...     # Here, we register a as dispatchable and mark it as an int
    ...     return (DispatchableInt(a),)
    >>> @ua.register_implementation(be, potato)
    ... def potato_impl(a, b):
    ...     return a, b
    >>> with ua.set_backend(be, coerce=True):
    ...     potato(1, '2')
    (-2, '2')
    """
    def __init__(self, value: Any):
        if type(self) is DispatchableInstance:
            raise RuntimeError('Do not instantiate this class directly, '
                               'only through the subclasses.')

        self.value = value


def all_of_type(arg_type: Type[DispatchableInstance]):
    """
    A convenience dispatcher to mark all of the unmarked dispatchables from an argument extractor as one type.

    Examples
    --------
    >>> import uarray as ua
    >>> class DispatchableInt(ua.DispatchableInstance):
    ...     pass
    >>> be = ua.TypeCheckBackend((int,))
    >>> # All ints piped to -2
    >>> be.register_convertor(DispatchableInt, lambda x: -2)
    >>> def potato_rd(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs
    >>> @ua.create_multimethod(potato_rd)
    ... @ua.all_of_type(DispatchableInt)
    ... def potato(a, b):
    ...     # Here, we register a as dispatchable and mark it as an int
    ...     return (a,)
    >>> @ua.register_implementation(be, potato)
    ... def potato_impl(a, b):
    ...     return a, b
    >>> with ua.set_backend(be, coerce=True):
    ...     potato(1, '2')
    (-2, '2')
    """
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            extracted_args = func(*args, **kwargs)
            return tuple(arg_type(arg) for arg in extracted_args if not isinstance(arg, DispatchableInstance))

        return inner

    return outer
