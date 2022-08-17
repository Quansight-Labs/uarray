from typing import Any, Callable, Sequence
import inspect
from dataclasses import dataclass
import functools

import uarray


@dataclass(frozen=True)
class DispatchableArg:
    name: str
    dispatch_type: Any
    coercible: bool = True


def _generate_arg_extractor_replacer(
    func: Callable, dispatch_args: Sequence[DispatchableArg]
):
    sig = inspect.signature(func)
    dispatchable_args = []

    annotations = {}
    for d in dispatch_args:
        if d.name in annotations:
            raise ValueError(f"Duplicate DispatchableArg annotation for '{d.name}'")

        annotations[d.name] = d

    for i, p in enumerate(sig.parameters.values()):
        ann = annotations.get(p.name, None)
        if ann is None:
            continue

        dispatchable_args.append((i, ann))

    @functools.wraps(func)
    def arg_extractor(*args, **kwargs):
        # Raise appropriate TypeError if the signature doesn't match
        func(*args, **kwargs)

        dispatchables = []
        for i, ann in dispatchable_args:
            if len(args) > i:
                dispatchables.append(
                    uarray.Dispatchable(args[i], ann.dispatch_type, ann.coercible)
                )
            elif ann.name in kwargs:
                dispatchables.append(
                    uarray.Dispatchable(
                        kwargs[ann.name], ann.dispatch_type, ann.coercible
                    )
                )

        return tuple(dispatchables)

    def arg_replacer(args, kwargs, dispatchables):
        new_args = list(args)
        new_kwargs = kwargs.copy()
        cur_idx = 0

        for i, ann in dispatchable_args:
            if len(args) > i:
                new_args[i] = dispatchables[cur_idx]
                cur_idx += 1
            elif ann.name in kwargs:
                new_kwargs[ann.name] = dispatchables[cur_idx]
                cur_idx += 1

        assert cur_idx == len(dispatchables)
        return tuple(new_args), new_kwargs

    return arg_extractor, arg_replacer
