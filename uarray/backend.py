from typing import Callable, Iterable, Dict, Tuple, Any, Set, Optional, Type, Union, List
import inspect
from contextvars import ContextVar
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
        This is a callable that extracts the arguments over which the dispatch will be performed.
    argument_replacer : ArgumentReplacerType
        This takes in args, kwargs and dispatchable args, and replaces all dispatchable arguments within
        the args and kwargs, and then returns them.
    default : Optional[Callable], optional
        This is the default implementation for this multimethod, possibly in terms of other multimethods.

    Examples
    --------
    >>> import uarray as ua

    We first define an argument extractor, which extracts the relevant dispatchable arguments from the
    arguments of the function. Note that the extracted arguments don't have to be direct arguments to
    the function, they can be anything contained within as well. For example, if ``a`` was a ``list`` and
    we wanted to treat everything within it as dispatchable, we could return ``tuple(a)``.

    >>> def potato_extractor(a, b):
    ...     return (a,) # b is not is dispatchable, so we return a only, as a tuple.

    Next, we define the argument replacer. This replaces the dispatchable arguments within the function
    with the ones that are supplied externally.

    >>> def potato_replacer(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs

    The next step is to define an (optional) default implementation of the method.

    >>> def potato_impl(a, b):
    ...     # The default implementation passes through all arguments
    ...     return a, b

    Then, we build the :obj:`MultiMethod` from these and test it.

    >>> potato_mm = ua.MultiMethod(potato_extractor, potato_replacer, default=potato_impl)
    >>> potato_mm(1, '2')
    (1, '2')

    See Also
    --------
    Backend
        A way to override :obj:`MultiMethod` s.

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
        result = NotImplemented
        for options in _backend_order():
            result = options.backend.try_backend(self, args, kwargs, coerce=options.coerce)

            if result is not NotImplemented:
                break
        else:
            if self.default is not None:
                result = self.default(*args, **kwargs)

        if result is NotImplemented:
            raise BackendNotImplementedError('No selected backends had an implementation for this method.')

        return result

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
        return self.method(self.instance, *args, **kwargs)

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
    default : Optional[Callable], optional
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


ImplementationType = Callable[[MultiMethod, Iterable, Dict, Iterable], Any]
InstanceStubType = Any
ConvertorType = Callable[["DispatchableInstance"], Any]
MethodLookupType = Dict[Optional[MultiMethod], ImplementationType]
TypeLookupType = Dict[Type["DispatchableInstance"], ConvertorType]
InstanceLookupType = Dict["DispatchableInstance", InstanceStubType]


class Backend:
    """
    A class you can register methods against.

    Examples
    --------
    We start with the example from the :obj:`MultiMethod` documentation, but with the
    difference that we *don't* provide a default implementation.

    >>> import uarray as ua
    >>> def potato_extractor(a, b):
    ...     return (a,) # b is not is dispatchable, so we return a only, as a tuple.

    >>> def potato_replacer(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs
    >>> potato_mm = ua.MultiMethod(potato_extractor, potato_replacer)
    >>> potato_mm(1, '2')
    Traceback (most recent call last):
        ...
    uarray.backend.BackendNotImplementedError: ...

    Notice how we get an error when we try to invoke a :obj:`MultiMethod` without a default
    implementation. Let's see what happens when we add a backend:

    >>> be = ua.Backend()
    >>> @ua.register_implementation(potato_mm, be)
    ... def potato_impl(a, b):
    ...     if not isinstance(a, int):
    ...         return NotImplemented
    ...     return a, b
    >>> with ua.set_backend(be):
    ...     potato_mm(1, '2')
    (1, '2')
    >>> with ua.set_backend(be):
    ...     potato_mm('1', '2')
    Traceback (most recent call last):
        ...
    uarray.backend.BackendNotImplementedError: ...
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
        implementation : ImplementationType
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
        >>> be = ua.Backend()  # Define "supported dispatchable types"
        >>> def potato_impl(method, args, kwargs, dispatchable_args):
        ...     # method will be potato
        ...     return args, kwargs
        >>> be.register_implementation(potato, potato_impl)
        >>> with ua.set_backend(be):
        ...     potato(1, '2')
        ((1, '2'), {})
        >>> be.register_implementation(potato, potato_impl)
        Traceback (most recent call last):
            ...
        ValueError: ...
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
        implementation : ImplementationType
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
        >>> be = ua.Backend()
        >>> # All ints piped to -2
        >>> be.register_convertor(DispatchableInt, lambda x: -2)
        >>> def potato_rd(args, kwargs, dispatch_args):
        ...     # This replaces a within the args/kwargs
        ...     return dispatch_args + args[1:], kwargs
        >>> @ua.create_multimethod(potato_rd)
        ... def potato(a, b):
        ...     # Here, we register a as dispatchable and mark it as an int
        ...     return (DispatchableInt(a),)
        >>> @ua.register_implementation(potato, be)
        ... def potato_impl(a, b):
        ...     return a, b
        >>> with ua.set_backend(be, coerce=True):
        ...     potato(1, '2')
        (-2, '2')
        >>> be.register_convertor(DispatchableInt, lambda x: -2)
        Traceback (most recent call last):
            ...
        ValueError: ...
        """
        if dispatch_type in self._convertors:
            raise ValueError('Cannot register a different convertor once one is already registered.')

        self._convertors[dispatch_type] = convertor

    def replace_dispatchables(self, method: MultiMethod, args, kwargs, coerce: Optional[bool] = False):
        """
        Replace dispatchables for a this method, using the convertor, if coercion is used.

        Parameters
        ----------
        method : MultiMethod
            The method to replace the args/kwargs for.
        args, kwargs
            The args and kwargs to replace.
        coerce : Optional[bool], optional
            Whether or not to coerce the arrays during replacement. Default is False.

        Returns
        -------
        args, kwargs: The replaced args/kwargs.
        dispatchable_args: The extracted dispatchable args.
        """
        dispatchable_args = method.argument_extractor(*args, **kwargs)
        replaced_args: List = []
        filtered_dispatchable_args: List = []
        for arg in dispatchable_args:
            replaced_arg = self._replace_single(arg, coerce=coerce)
            replaced_args.append(replaced_arg)

            if not isinstance(arg, DispatchableInstance):
                filtered_dispatchable_args.append(replaced_arg)
            elif type(arg) in self._convertors:
                filtered_dispatchable_args.append(type(arg)(replaced_arg))

        args, kwargs = method.argument_replacer(args, kwargs, tuple(replaced_args))
        return args, kwargs, filtered_dispatchable_args

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

    def try_backend(self, method: MultiMethod, args: Tuple, kwargs: Dict, coerce: bool):
        """
        Try this backend for a given args and kwargs. Returns either a
        result or ``NotImplemented``. All exceptions are propagated.
        """
        current_args, current_kwargs, dispatchable_args = self.replace_dispatchables(
            method, args, kwargs, coerce=coerce)

        result = NotImplemented

        if method in self._implementations:
            result = self._implementations[method](method, current_args, current_kwargs, dispatchable_args)

        if result is NotImplemented and None in self._implementations:
            result = self._implementations[None](method, current_args, current_kwargs, dispatchable_args)

        if result is NotImplemented and method.default is not None:
            try:
                with set_backend(self, coerce=coerce, only=True):
                    result = method.default(*current_args, **current_kwargs)
            except BackendNotImplementedError:
                pass

        return result


_backends: Set[Backend] = set()


class BackendOptions:
    def __init__(self, backend: Backend, coerce: bool = False, only: bool = True, options: Optional[Any] = None):
        """
        The backend plus any additional options associated with it.

        Parameters
        ----------
        backend : Backend
            The associated backend.
        coerce: bool, optional
            Whether or not the backend is being coerced. Implies ``only``.
        only: bool, optional
            Whether or not this is the only backend to try.
        options: Optional[Any]
            Any additional options to pass to the backend.
        """
        self.backend = backend
        self.coerce = coerce
        self.only = only or coerce
        self.options = options


def _backend_order() -> Iterable[BackendOptions]:
    be = _current_backend.get()
    yield from _backend_order_iter()
    _current_backend.set(be)


def _backend_order_iter() -> Iterable[BackendOptions]:
    skip = _skipped_backend.get()
    pref = _preferred_backend.get()

    for options in pref:
        _current_backend.set(options)
        if options.backend not in skip:
            yield options

        if options.only:
            return

    for backend in _backends:
        be = BackendOptions(backend)
        _current_backend.set(be)
        yield be


_preferred_backend: ContextVar[Tuple[BackendOptions, ...]] = ContextVar('_preferred_backend', default=())
_skipped_backend: ContextVar[Set[Backend]] = ContextVar('_skipped_backend', default=set())
_current_backend: ContextVar[Optional[BackendOptions]] = ContextVar('_current_backend', default=None)


def get_current_backend() -> Optional[BackendOptions]:
    """
    Returns the current backend, with options. ``None`` indicates that
    there is no possible backend that can be used.

    See Also
    --------
    BackendOptions: The backend, plus any associated options.
    set_backend: Set the current backend.
    """
    be = _current_backend.get()

    if be is None:
        return BackendOptions(next(iter(_backends))) if len(_backends) else None

    return be


class set_backend:
    """
    A context manager that sets the preferred backend. Uses :obj:`BackendOptions` to create
    the options, and sets the backend with the preferred options.

    Parameters
    ----------
    backend : Backend
        The backend to set.

    See Also
    --------
    BackendOptions: The backend plus options.
    get_current_backend: Get the current backend.
    skip_backend: A context manager that allows skipping of backends.
    DispatchableInstance: Items to be coerced must be marked by a DispatchableInstance.
    """

    def __init__(self, backend: Backend, *args, **kwargs):
        self.value = BackendOptions(backend, *args, **kwargs)

    def __enter__(self):
        self.token = _preferred_backend.set((self.value,) + _preferred_backend.get())

    def __exit__(self, exception_type, exception_value, traceback):
        _preferred_backend.reset(self.token)


class skip_backend:
    def __init__(self, backend: Backend):
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
        self.backend = backend
        self.token = None

    def __enter__(self):
        new_skipped = set(_skipped_backend.get())
        new_skipped.add(self.backend)
        self.token = _skipped_backend.set(new_skipped)

    def __exit__(self, exception_type, exception_value, traceback):
        _skipped_backend.reset(self.token)


CompatCheckType = Callable[[Iterable["DispatchableInstance"]], bool]


def register_implementation(method: MultiMethod, backend: Backend, compat_check: Optional[CompatCheckType] = None):
    """
    Create an implementation for a given backend/method. The implementation
    should have the same signature as the method, or perhaps with some optional
    arguments missing. The ``compat_check`` parameter takes in an iterable
    of dispatchable instances and returns a :obj:`bool` indicating whether or not
    the backend supports this configuration.
    """
    def wrapper(func):
        @functools.wraps(func)
        def inner(method, args, kwargs, dispatchable_args):
            if compat_check is not None and not compat_check(dispatchable_args):
                return NotImplemented
            return func(*args, **kwargs)

        backend.register_implementation(method, inner)

        return func

    return wrapper


def register_backend(backend: Backend):
    """
    This utility method registers the backend for permanent use. It
    will be tried in the list of backends automatically, unless the
    ``only`` flag is set on a backend.

    Parameters
    ----------
    backend : Backend
        The backend to register.
    """
    _backends.add(backend)


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
    >>> be = ua.Backend()
    >>> # All ints piped to -2
    >>> be.register_convertor(DispatchableInt, lambda x: -2)
    >>> def potato_rd(args, kwargs, dispatch_args):
    ...     # This replaces a within the args/kwargs
    ...     return dispatch_args + args[1:], kwargs
    >>> @ua.create_multimethod(potato_rd)
    ... def potato(a, b):
    ...     # Here, we register a as dispatchable and mark it as an int
    ...     return (DispatchableInt(a),)
    >>> @ua.register_implementation(potato, be)
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
    >>> be = ua.Backend()
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
    >>> @ua.register_implementation(potato, be)
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
