#%%
import typing
import dataclasses
import typing_extensions
import collections.abc

T = typing.TypeVar("T")

T_partial = typing.TypeVar("T_partial", bound=NotImplemented, covariant=True)

T_partial_callable = typing.TypeVar(
    "T_partial_callable", bound=typing.Callable[..., NotImplemented]
)


class ChainCallable:
    """
    Like ChainMap but for callables. Combines a bunch of functions
    into one function, where each are tried in order on the arguments
    until one returns something other than `NotImplemented`.
    """

    def __init__(self, *callables):
        self.callables = callables

    def __call__(self, *args, **kwargs):
        for callable in self.callables:
            res = callable(*args, **kwargs)
            if res is not NotImplemented:
                return res
        return NotImplemented


class ChainCallableMap(collections.abc.Mapping):
    def __init__(self, *callable_maps):
        self.callable_maps = callable_maps

    def __getitem__(self, key):
        return ChainCallable(
            *(callable_map[key] for callable_map in self.callable_maps)
        )

    def __len(self):
        s = set()
        for callable_map in self.callable_maps:
            s.update(callable_map.keys())
        return len(s)

    def __iter__(self):
        s = set()
        for callable_map in self.callable_maps:
            s.update(callable_map.keys())
        return iter(s)


Replacement = typing.Callable[[Node], typing.Union[Node, NotImplemented]]
ReplacmentMapping = typing.Mapping[str, Replacement]


class CompilationStrategy:
    mapping: typing.Mapping[str, Replacement]


T = typing.TypeVar("T")
T_collection = typing.TypeVar("T_collection", bound=typing.Collection)


@dataclasses.dataclass(eq=False)
class Node(typing.Generic[T_collection]):
    name: str
    args: T_collection

    def replace_with(self, node: "Node") -> None:
        self.name = node.name
        self.args = node.args  # type: ignore

    def could_equal(self, other_node: "Node") -> bool:
        return self.name == other_node.name and len(self.args) == len(other_node.args)


ArgNames = typing.Collection[typing.Optional[str]]


@dataclasses.dataclass(frozen=True)
class Replacement:
    name: str
    arg_names: ArgNames
    replace: typing.Callable[..., Node]


Replacements = typing.Collection[Replacement]


def args_match(args: typing.Collection, arg_names: ArgNames) -> bool:
    if len(args) != len(arg_names):
        return False
    for arg, arg_name in zip(args, arg_names):
        if arg_name is not None and (not isinstance(arg, Node) or arg.name != arg_name):
            return False
    return True


class NoReplacementFound(Exception):
    pass


def find_relevent_replacement(
    node: Node, replacements: Replacements
) -> typing.Tuple[Node, Replacement]:
    for replacement in replacements:
        if node.name != replacement.name or not args_match(
            node.args, replacement.arg_names
        ):
            continue
        return node, replacement
    for arg in node.args:
        if isinstance(arg, Node):
            try:
                return find_relevent_replacement(arg, replacements)
            except NoReplacementFound:
                pass
    raise NoReplacementFound


def replace(node: Node, replacements: Replacements):
    while True:
        try:
            replace_node, replacement = find_relevent_replacement(node, replacements)
        except NoReplacementFound:
            return
        new_node = replacement.replace(*replace_node.args)  # type: ignore
        replace_node.replace_with(new_node)
        yield replace_node, replacement


# def replace_variables(
#     root: Node, replacements: typing.Dict[VariableNode, Node]
# ) -> None:
#     """
#     Replaces all instances of variable in root with the replacement node
#     """
#     for variable, node in replacements.items():
#         if variable is node:
#             root.replace_with(variable)
#             return
#     for arg in root.args:
#         # don't replace on primitive edges
#         if isinstance(arg, Node):
#             replace_variables(arg, replacements)


# class ReplacementPattern(typing.NamedTuple):
#     """
#     Holds a replacement pattern.
#     """

#     pattern: Node
#     replacement: Node
#     variables: typing.Set[VariableNode]


# class CannotMatchError(Exception):
#     def __init__(self, root, pattern):
#         self.root = root
#         self.pattern = pattern


# def match_variables(
#     root: Node, pattern: Node, variables: typing.Set[VariableNode]
# ) -> typing.Dict[VariableNode, Node]:
#     """
#     Returns a mapping of variables to the values at them, if it matches.

#     Otherwise raises CannotMatchError.
#     """
#     # first we check whether the pattern is a variable. If so
#     for variable in variables:
#         if pattern is variable:
#             return {variable: root}
#     if not root.could_equal(pattern):
#         raise CannotMatchError(root, pattern)
#     mapping = {}
#     for new_root, new_pattern in zip(root.args, pattern.args):
#         if isinstance(new_root, Node) and isinstance(new_pattern, Node):
#             mapping.update(match_variables(new_root, new_pattern, variables))
#         # if one of them is a primitive type, then the other should be as well and they should be equal
#         elif new_root != new_pattern:
#             raise CannotMatchError(new_root, new_pattern)
#     return mapping


# def trigger_replacement(root: Node, pattern: ReplacementPattern) -> Node:
#     variables = match_variables(root, pattern.pattern, pattern.variables)
#     return replace_variables(pattern.replacement, variables)
