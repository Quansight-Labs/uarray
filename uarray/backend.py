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

ArgumentExtractorType = Callable[..., Tuple["DispatchableInstance", ...]]
ArgumentReplacerType = Callable[[Tuple, Dict, Tuple], Tuple[Tuple, Dict]]


class BackendNotImplementedError(NotImplementedError):
    """
    An exception that is thrown when no compatible backend is found for a method.
    """


def create_multimethod(*args, **kwargs):
    def wrapper(a):
        return generate_multimethod(a, *args, **kwargs)

    return wrapper


def generate_multimethod(
    argument_extractor: ArgumentExtractorType,
    argument_replacer: ArgumentReplacerType,
    domain: str,
    default: Optional[Callable] = None,
):
    @functools.wraps(argument_extractor)
    def inner(*args, **kwargs):
        args, kwargs = _canonicalize(argument_extractor, args, kwargs)
        errors = []

        for options in _backend_order(domain):
            a, kw, da = replace_dispatchables(
                options.backend, args, kwargs, coerce=options.coerce
            )

            result = options.backend.__ua_function__(inner, a, kw, da)

            if result is not NotImplemented:
                return result

            if default is not None:
                try:
                    with set_backend(options.backend, only=True, coerce=options.coerce):
                        result = default(*a, **kw)
                except BackendNotImplementedError as e:
                    errors.append(e)

                if result is not NotImplemented:
                    return result

        raise BackendNotImplementedError(
            "No selected backends had an implementation for this function.", errors
        )

    def replace_dispatchables(backend, args, kwargs, coerce: Optional[bool] = False):
        dispatchable_args = argument_extractor(*args, **kwargs)
        replaced_args: List = []
        filtered_args: List = []
        for arg in dispatchable_args:
            replaced_arg = (
                backend.__ua_coerce__(arg.value, arg.dispatch_type)
                if isinstance(arg, DispatchableInstance)
                else NotImplemented
            )

            if replaced_arg is not NotImplemented:
                filtered_args.append(
                    DispatchableInstance(replaced_arg, dispatch_type=arg.dispatch_type)
                )
                replaced_args.append(replaced_arg)
            else:
                replaced_args.append(
                    arg if not isinstance(arg, DispatchableInstance) else arg.value
                )

        args, kwargs = argument_replacer(args, kwargs, tuple(replaced_args))
        return args, kwargs, filtered_args

    inner._coerce_args = replace_dispatchables  # type: ignore

    return inner


class _BackendOptions:
    def __init__(
        self,
        backend,
        coerce: bool = False,
        only: bool = False,
        options: Optional[Any] = None,
    ):
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
        options: Optional[Any], optional
            Any additional options to pass to the backend.
        """
        self.backend = backend
        self.coerce = coerce
        self.only = only or coerce
        self.options = options


_backends: Dict[str, Any] = {}


def _backend_order(module: str) -> Iterable[_BackendOptions]:
    skip = _get_skipped_backends(module).get()
    pref = _get_preferred_backends(module).get()

    for options in pref:
        if options.backend not in skip:
            yield options

            if options.only:
                return

    if module in _backends:
        yield _BackendOptions(_backends[module])


def _get_preferred_backends(module: str) -> ContextVar[Tuple[_BackendOptions, ...]]:
    if module not in _preferred_backend:
        _preferred_backend[module] = ContextVar(
            f"_preferred_backend[{module}]", default=()
        )
    return _preferred_backend[module]


def _get_skipped_backends(module: str) -> ContextVar[Set]:
    if module not in _skipped_backend:
        _skipped_backend[module] = ContextVar(
            f"_skipped_backend[{module}]", default=set()
        )
    return _skipped_backend[module]


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
    get_current_backend: Get the current backend.
    skip_backend: A context manager that allows skipping of backends.
    DispatchableInstance: Items to be coerced must be marked by a DispatchableInstance.
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


def register_canonical_backend(domain: str, backend):
    """
    This utility method registers the backend for permanent use. It
    will be tried in the list of backends automatically, unless the
    ``only`` flag is set on a backend.

    Parameters
    ----------
    backend
        The backend to register.
    """
    if domain in _backends:
        raise ValueError("Backend already registered for this domain.")

    _backends[domain] = backend


class DispatchableInstance:
    def __init__(self, value, dispatch_type):
        self.value = value
        self.dispatch_type = dispatch_type

    def __str__(self):
        return f"<Dispatchable, type={str(self.dispatch_type)}, value={str(self.value)}"


def mark_as(dispatch_type):
    return functools.partial(DispatchableInstance, dispatch_type=dispatch_type)


def all_of_type(arg_type):
    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            extracted_args = func(*args, **kwargs)
            return tuple(
                DispatchableInstance(arg, arg_type)
                if not isinstance(arg, DispatchableInstance)
                else arg
                for arg in extracted_args
            )

        return inner

    return outer
