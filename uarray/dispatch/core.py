import collections
import collections.abc
import contextvars
import dataclasses
import functools
import typing
import copy

__all__ = [
    "Operation",
    "Box",
    "global_context",
    "ReplacementType",
    "ContextType",
    "MutableContextType",
    "KeyType",
    "children",
    "replace_generator",
    "key",
    "ChildrenType",
    "replace",
    "ChainCallable",
    "MapChainCallable",
    "ChainCallableMap",
    "default_context",
]

T = typing.TypeVar("T")


T_cov = typing.TypeVar("T_cov", covariant=True)


@dataclasses.dataclass
class Box(typing.Generic[T_cov]):
    value: T_cov


ReplacementType = typing.Callable[[Box], Box]


ChildrenType = typing.Sequence[Box]


@functools.singledispatch
def children(node) -> ChildrenType:
    return ()


@children.register
def tuple_children(op: tuple) -> tuple:
    return op


KeyType = object


@functools.singledispatch
def key(node: T) -> KeyType:
    return type(node)


T_args = typing.TypeVar("T_args", bound=ChildrenType)


@dataclasses.dataclass(frozen=True)
class Operation(typing.Generic[T_args]):
    name: object
    args: T_args


@children.register(Operation)
def operation_children(op: Operation[T_args]) -> T_args:
    return op.args


@key.register
def operation_key(op: Operation) -> object:
    return op.name


ContextType = typing.Mapping[KeyType, ReplacementType]
MutableContextType = typing.MutableMapping[KeyType, ReplacementType]


class ChainCallable:
    """
    Like ChainMap but for callables. Combines a bunch of functions
    into one function, where each are tried in order on the arguments
    until one returns something other than `NotImplemented`.
    """

    def __init__(self, *callables: ReplacementType):
        self.callables = list(callables)

    def __call__(self, arg: Box) -> Box:
        for callable in self.callables:
            res = callable(arg)
            if res is not NotImplemented:
                return res
        return NotImplemented


class MapChainCallable(collections.abc.MutableMapping):
    """
    Mutable mapping of keys to a list of replacements.

    Setting a key adds the new replacement to the list, instead of overriding
    the existing ones.
    """

    def __init__(self):
        self.dict: typing.MutableMapping[
            KeyType, ChainCallable
        ] = collections.defaultdict(ChainCallable)

    def __setitem__(self, key: KeyType, value: ReplacementType) -> None:
        self.dict[key].callables.append(value)

    def __getitem__(self, key: KeyType) -> ReplacementType:
        return self.dict[key]

    def __delitem__(self, key: KeyType) -> None:
        del self.dict[key]

    def __iter__(self) -> typing.Iterator[KeyType]:
        return iter(self.dict)

    def __len__(self) -> int:
        return len(self.dict)


class ChainCallableMap(collections.abc.Mapping):
    def __init__(self, *callable_maps: ContextType):
        self.callable_maps = list(callable_maps)

    def __getitem__(self, key: KeyType) -> ReplacementType:
        return ChainCallable(
            *(
                callable_map[key]
                for callable_map in self.callable_maps
                if key in callable_map
            )
        )

    def __len__(self) -> int:
        s: typing.Set[KeyType] = set()
        for callable_map in self.callable_maps:
            s.update(callable_map.keys())
        return len(s)

    def __iter__(self) -> typing.Iterator[KeyType]:
        s: typing.Set[KeyType] = set()
        for callable_map in self.callable_maps:
            s.update(callable_map.keys())
        return iter(s)

    def append(self, context: ContextType):
        self.callable_maps.append(context)


default_context = ChainCallableMap()


global_context: contextvars.ContextVar[ContextType] = contextvars.ContextVar(
    "uarray.dispatch.global_context", default=default_context
)


def replace_inplace(box: Box) -> None:
    while replace_inplace_once(box) is not None:
        pass


def replace(box: Box) -> Box:
    box = copy.deepcopy(box)
    while replace_inplace_once(box) is not None:
        box = copy.deepcopy(box)
    return box


def replace_generator(box: Box) -> typing.Iterator[typing.Tuple[Box, Box]]:
    box = copy.deepcopy(box)
    while True:
        replaced_box = replace_inplace_once(box)
        if replaced_box is None:
            return
        yield replaced_box, box
        box = copy.deepcopy(box)


def replace_inplace_generator(box: Box) -> typing.Iterator[Box]:
    """
    Keeps calling replacemnts on the node, or it's children, until no more match.

    Returns a sequence of the boxes that are mutated during each replacement.
    """
    while True:
        replaced_box = replace_inplace_once(box)
        if replaced_box is None:
            return
        yield replaced_box


def replace_inplace_once(box: Box) -> typing.Optional[Box]:
    """
    Tries to replace the box and it's children,
    returning the box that was replaced or None if no replacement could be matched.
    """
    for child in children(box.value):
        replaced_child = replace_inplace_once(child)
        if replaced_child:
            return replaced_child

    context = global_context.get()
    try:
        replacement = context[key(box.value)]
    except KeyError:
        # no replacements registered for node
        return None

    # computes the new node and copies it over
    new_box = replacement(box)

    if new_box == NotImplemented:
        return None

    box.value = new_box.value

    return box
