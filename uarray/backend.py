from typing import (
    Callable,
    Iterable,
    Dict,
    Tuple,
    Any,
    Set,
    Optional,
    Type,
    Union,
    List,
)
import inspect
from contextvars import ContextVar
import functools
import contextlib

ArgumentExtractorType = Callable[..., Tuple["Dispatchable", ...]]
ArgumentReplacerType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class BackendNotImplementedError(NotImplementedError):
    """
    An exception that is thrown when no compatible backend is found for a method.
    """


def create_multimethod(*args, **kwargs):
    """
    Creates a decorator for generating multimethods.

    This function creates a decorator that can be used with an argument
    extractor in order to generate a multimethod. Other than for the
    argument extractor, all arguments are passed on to
    :obj:`generate_multimethod`.

    See Also
    --------
    generate_multimethod
        Generates a multimethod.
    """

    def wrapper(a):
        return generate_multimethod(a, *args, **kwargs)

    return wrapper


def generate_multimethod(
    argument_extractor: ArgumentExtractorType,
    argument_replacer: ArgumentReplacerType,
    domain: str,
    default: Optional[Callable] = None,
):
    """
    Generates a multimethod.

    Parameters
    ----------
    argument_extractor : ArgumentExtractorType
        A callable which extracts the dispatchable arguments. Extracted arguments
        should be marked by the :obj:`Dispatchable` class. It has the same signature
        as the desired multimethod.
    argument_replacer : ArgumentReplacerType
        A callable with the signature (args, kwargs, dispatchables), which should also
        return an (args, kwargs) pair with the dispatchables replaced inside the args/kwargs.
    domain : str
        A string value indicating the domain of this multimethod.
    default: Optional[Callable], optional
        The default implementation of this multimethod, where ``None`` (the default) specifies
        there is no default implementation.

    Examples
    --------
    In this example, ``a`` is to be dispatched over, so we return it, while marking it as an ``int``.
    The trailing comma is needed because the args have to be returned as an iterable.

    >>> def override_me(a, b):
    ...   return Dispatchable(a, int),

    Next, we define the argument replacer that replaces the dispatchables inside args/kwargs with the
    supplied ones.

    >>> def override_replacer(args, kwargs, dispatchables):
    ...     return (dispatchables[0], args[1]), {}

    Next, we define the multimethod.

    >>> overridden_me = generate_multimethod(
    ...     override_me, override_replacer, "ua_examples"
    ... )

    Notice that there's no default implementation, unless you supply one.

    >>> overridden_me(1, "a")
    Traceback (most recent call last):
        ...
    uarray.backend.BackendNotImplementedError: ...
    >>> overridden_me2 = generate_multimethod(
    ...     override_me, override_replacer, "ua_examples", default=lambda x, y: (x, y)
    ... )
    >>> overridden_me2(1, "a")
    (1, 'a')

    See Also
    --------
    uarray
        See the module documentation for how to override the method by creating backends.
    """

    @functools.wraps(argument_extractor)
    def inner(*args, **kwargs):
        # args, kwargs = _canonicalize(argument_extractor, args, kwargs)
        dispatchable_args = argument_extractor(*args, **kwargs)
        errors = []

        result = NotImplemented

        for options in _backend_order(domain):
            a, kw, da = replace_dispatchables(
                options.backend, args, kwargs, dispatchable_args, coerce=options.coerce
            )

            result = options.backend.__ua_function__(inner, a, kw, da)

            if result is NotImplemented:
                result = try_default(a, kw, options, errors)

            if result is not NotImplemented:
                break
        else:
            result = try_default(args, kwargs, None, errors)

        if result is NotImplemented:
            raise BackendNotImplementedError(
                "No selected backends had an implementation for this function.", errors
            )

        return result

    def try_default(args, kwargs, options, errors):
        if default is not None:
            try:
                if options is not None:
                    with set_backend(options.backend, only=True, coerce=options.coerce):
                        return default(*args, **kwargs)
                else:
                    return default(*args, **kwargs)
            except BackendNotImplementedError as e:
                errors.append(e)

        return NotImplemented

    def replace_dispatchables(
        backend, args, kwargs, dispatchable_args, coerce: Optional[bool] = False
    ):
        replaced_args: List = []
        filtered_args: List = []
        for arg in dispatchable_args:
            replaced_arg = backend.__ua_convert__(arg.value, arg.type, coerce=coerce)

            if replaced_arg is not NotImplemented:
                filtered_args.append(
                    Dispatchable(
                        replaced_arg, dispatch_type=arg.type, coercible=arg.coercible
                    )
                )
                replaced_args.append(replaced_arg)
            else:
                replaced_args.append(arg.value)

        args, kwargs = argument_replacer(args, kwargs, tuple(replaced_args))
        return args, kwargs, filtered_args

    inner._coerce_args = replace_dispatchables  # type: ignore

    return inner


class _BackendOptions:
    def __init__(self, backend, coerce: bool = False, only: bool = False):
        """
        The backend plus any additonal options associated with it.

        Parameters
        ----------
        backend : Backend
            The associated backend.
        coerce: bool, optional
            Whether or not the backend is being coerced. Implies ``only``.
        only: bool, optional
            Whether or not this is the only backend to try.
        """
        self.backend = backend
        self.coerce = coerce
        self.only = only or coerce


_backends: Dict[str, ContextVar] = {}


def _backend_order(domain: str) -> Iterable[_BackendOptions]:
    skip = _get_skipped_backends(domain).get()
    pref = _get_preferred_backends(domain).get()

    for options in pref:
        if options.backend not in skip:
            yield options

            if options.only:
                return

    if domain in _backends:
        yield _BackendOptions(_backends[domain])


def _get_preferred_backends(domain: str) -> ContextVar[Tuple[_BackendOptions, ...]]:
    if domain not in _preferred_backend:
        _preferred_backend[domain] = ContextVar(
            f"_preferred_backend[{domain}]", default=()
        )
    return _preferred_backend[domain]


def _get_skipped_backends(domain: str) -> ContextVar[Set]:
    if domain not in _skipped_backend:
        _skipped_backend[domain] = ContextVar(
            f"_skipped_backend[{domain}]", default=set()
        )
    return _skipped_backend[domain]


_preferred_backend: Dict[str, ContextVar[Tuple[_BackendOptions, ...]]] = {}
_skipped_backend: Dict[str, ContextVar[Set]] = {}


@contextlib.contextmanager
def set_backend(backend, *args, **kwargs):
    """
    A context manager that sets the preferred backend. Uses :obj:`BackendOptions` to create
    the options, and sets the backend with the preferred options.

    Parameters
    ----------
    backend
        The backend to set.

    See Also
    --------
    BackendOptions: The backend plus options.
    skip_backend: A context manager that allows skipping of backends.
    """
    options = _BackendOptions(backend, *args, **kwargs)
    pref = _get_preferred_backends(backend.__ua_domain__)
    token = pref.set((options,) + pref.get())

    try:
        yield
    finally:
        pref.reset(token)


@contextlib.contextmanager
def skip_backend(backend):
    """
    A context manager that allows one to skip a given backend from processing
    entirely. This allows one to use another backend's code in a library that
    is also a consumer of the same backend.

    Parameters
    ----------
    backend
        The backend to skip.

    See Also
    --------
    set_backend: A context manager that allows setting of backends.
    """
    skip = _get_skipped_backends(backend.domain)
    new = set(skip.get())
    new.add(backend)
    token = skip.set(new)

    try:
        yield
    finally:
        skip.reset(token)


def _canonicalize(f, args, kwargs):
    sig = inspect.signature(f)
    bargs = sig.bind(*args, **kwargs)
    # Pop out the named kwargs variable defaulting to {}
    ret_kwargs = bargs.arguments.pop(inspect.getfullargspec(f).varkw, {})
    # For all possible signature values
    for k, v in sig.parameters.items():
        # If the name exists in the bound arguments and has a default value
        if k in bargs.arguments and v.default is not v.empty:
            # Remove from the bound arguments dict
            val = bargs.arguments.pop(k)
            # If the value isn't the same as the default value add it to ret_kwargs
            if val is not v.default:
                ret_kwargs[k] = val

    # bargs.args here will be made up of what's left in bargs.arguments
    return bargs.args, ret_kwargs


def set_global_backend(domain: str, backend):
    """
    This utility method registers the backend for permanent use. It
    will be tried in the list of backends automatically, unless the
    ``only`` flag is set on a backend.

    Note that this method is not thread-safe.

    .. warning::
        We caution library authors against using this function in
        their code. We do *not* support this use-case. This function
        is meant to be used only by users themselves, or by a reference
        implementation, if one exists.

    Parameters
    ----------
    backend
        The backend to register.
    """
    _backends[domain] = backend


class Dispatchable:
    """
    A utility class which marks an argument with a specific dispatch type.


    Attributes
    ----------
    value
        The value of the Dispatchable.
    
    type
        The type of the Dispatchable.

    Examples
    --------
    >>> x = Dispatchable(1, str)
    >>> x
    <Dispatchable: type=<class 'str'>, value=1>

    See Also
    --------
    all_of_type
        Marks all unmarked parameters of a function.
    
    mark_as
        Allows one to create a utility function to mark as a given type.
    """

    def __init__(self, value, dispatch_type, coercible=True):
        self.value = value
        self.type = dispatch_type
        self.coercible = coercible

    def __str__(self):
        return (
            f"<{type(self).__name__}: type={repr(self.type)}, value={repr(self.value)}>"
        )

    __repr__ = __str__


def mark_as(dispatch_type):
    """
    Creates a utility function to mark something as a specific type.

    Examples
    --------
    >>> mark_int = mark_as(int)
    >>> mark_int(1)
    <Dispatchable: type=<class 'int'>, value=1>
    """
    return functools.partial(Dispatchable, dispatch_type=dispatch_type)


def all_of_type(arg_type):
    """
    Marks all unmarked arguments as a given type.

    Examples
    --------
    >>> @all_of_type(str)
    ... def f(a, b):
    ...     return a, Dispatchable(b, int)
    >>> f('a', 1)
    (<Dispatchable: type=<class 'str'>, value='a'>, <Dispatchable: type=<class 'int'>, value=1>)
    """

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            extracted_args = func(*args, **kwargs)
            return tuple(
                Dispatchable(arg, arg_type)
                if not isinstance(arg, Dispatchable)
                else arg
                for arg in extracted_args
            )

        return inner

    return outer
