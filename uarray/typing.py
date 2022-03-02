from typing import Any, Annotated, Callable
import typing
import inspect
from dataclasses import dataclass
import functools

import uarray


@dataclass(frozen=True)
class _DispatchableAnnotation:
    dispatch_type: Any
    coercible: bool = True


class Dispatchable:
    def __new__(cls, *args, **kwargs):
        raise TypeError("uarray.typing.Dispatchable cannot be instantiated")

    def __class_getitem__(cls, params):
        if not isinstance(params, tuple) or len(params) < 2:
            raise TypeError(
                "uarray.typing.Dispatchable[...] expects two or more arguments "
                "(type and and dispatch_type).")
        T = params[0]
        tail = params[1:]

        return Annotated[T, _DispatchableAnnotation(*tail)]


def _generate_arg_extractor_replacer(func: Callable):
    sig = inspect.signature(func)
    dispatchable_args = []
    dispatchable_kwargs = []

    for i, p in enumerate(sig.parameters.values()):
        if typing.get_origin(p.annotation) is not Annotated:
            continue
        dispatch_annotations = [a for a in typing.get_args(p.annotation)
                                if isinstance(a, _DispatchableAnnotation)]
        if len(dispatch_annotations) == 0:
            continue
        if len(dispatch_annotations) > 1:
            raise TypeError("Expected at most one Dispatchable annotation")

        ann = dispatch_annotations[0]

        if p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                      inspect.Parameter.POSITIONAL_OR_KEYWORD):
            dispatchable_args.append((i, ann))

        if p.kind in (inspect.Parameter.KEYWORD_ONLY,
                      inspect.Parameter.POSITIONAL_OR_KEYWORD):
            dispatchable_kwargs.append((p.name, ann))

    @functools.wraps(func)
    def arg_extractor(*args, **kwargs):
        # Raise appropriate TypeError if the signature doesn't match
        func(*args, **kwargs)

        dispatchables = []
        for i, ann in dispatchable_args:
            if len(args) > i:
                dispatchables.append(uarray.Dispatchable(
                    args[i], ann.dispatch_type, ann.coercible))

        for name, ann in dispatchable_kwargs:
            if name in kwargs:
                dispatchables.append(uarray.Dispatchable(
                    kwargs[name], ann.dispatch_type, ann.coercible))

        return tuple(dispatchables)


    def arg_replacer(args, kwargs, dispatchables):
        new_args = list(args)
        new_kwargs = kwargs.copy()
        cur_idx = 0

        for i, ann in dispatchable_args:
            if len(args) > i:
                new_args[i] = dispatchables[cur_idx]
                cur_idx += 1

        for name, ann in dispatchable_kwargs:
            if name in kwargs:
                new_kwargs[name] = dispatchables[cur_idx]
                cur_idx += 1
        assert cur_idx == len(dispatchables)
        return tuple(new_args), new_kwargs

    return arg_extractor, arg_replacer
