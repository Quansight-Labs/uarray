# import typing
# import typing_extensions
# import dataclasses
# import abc
# import inspect


# from .core import *

# __all__ = ["NoMatch", "Spec", "SpecReplacement"]

# T = typing.TypeVar("T")


# class NoMatch(Exception):
#     pass


# @dataclasses.dataclass
# class Spec:
#     """
#     Types of children, for matching and unwrapping
#     """

#     types: typing.Sequence[typing.Type]
#     rest_type: typing.Optional[typing.Type]

#     def process_children(self, children_: ChildrenType) -> typing.Iterable:
#         for i, child in enumerate(children_):
#             try:
#                 child_type = self.types[i]
#             except IndexError:
#                 if self.rest_type is None:
#                     raise NoMatch
#                 child_type = self.rest_type
#             if isinstance(child.value, child_type):
#                 yield child.value
#             raise NoMatch

#     @classmethod
#     def from_sig(cls, sig: inspect.Signature) -> Spec:
#         types: typing.List[typing.Type] = []
#         rest_type: typing.Optional[typing.Type] = None
#         for param in sig.parameters.values():
#             if param.default:
#                 raise NotImplementedError
#             if param.annotation == inspect.Parameter.empty:
#                 raise NotImplementedError
#             if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
#                 types.append(param.annotation)
#             elif param.kind == inspect.Parameter.VAR_POSITIONAL:
#                 rest_type = param.annotation
#             else:
#                 raise NotImplementedError
#         return cls(types, rest_type)


# @dataclasses.dataclass
# class SpecReplacement(typing.Generic[T]):
#     fn: typing.Callable[..., T]
#     spec: Spec

#     def __name__(self):
#         return self.fn.__name__

#     def __call__(self, node: Box) -> Box[T]:
#         try:
#             return Box(self.fn(*self.spec.process_children(children(node))))
#         except NoMatch:
#             return NotImplemented

#     @classmethod
#     def from_function(cls, fn: typing.Callable[..., T]) -> SpecReplacement[T]:
#         return cls(fn, Spec.from_sig(inspect.signature(fn)))


# """
# When are things really instantiated? Let's create custom things and try them out.
# """

# def implements(context: MutableContextType) -> typing.Callable[[typing.Callable], None]:
#     """
#     Used to create and register a replacement baesd on the type of it's arguments.

#     If the arguments are any type besides `Node`, it is assumed they are `ValueArgs`
#     of some type.

#     @implements(ctx)
#     def some_node_name(arg, arg1: Node[SomeArgType], arg2: int) -> float:
#         ...
#     """

#     def implements_inner(fn: typing.Callable) -> None:
#         fn_name = fn.__name__

#         signature = inspect.signature(fn)

#         arg_translations = [
#             translate_arg_type(paramater) for paramater in signature.parameters.values()
#         ]

#         return_translation = translate_return_type(inspect.return_annotation)

#         def replacement(node: Node) -> OptionalNodeType:
#             if len(arg_translations) != len(node.args):
#                 return NotImplemented

#             args = []
#             for translate, arg in zip(arg_translations, node.args):
#                 translated_arg = translate(arg)
#                 if translated_arg is NotImplemented:
#                     return NotImplemented
#                 args.append(translated_arg)

#             ret = fn(*args)
#             return return_translation(ret)

#         context[fn_name] = replacement

#     return implements_inner


# def translate_arg_type(
#     parameter: inspect.Parameter
# ) -> typing.Callable[[Node], OptionalNodeType]:
#     """
#     Translates a type extracted from the arg signature to a callable
#     that takes in an input node representing that arg and returns
#     some transformed version of it for use in a function, or NotImplemented
#     if it isn't the right type.
#     """
#     if parameter.default:
#         raise NotImplementedError("Default parameters not supported")

#     if parameter.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
#         raise NotImplementedError("Only positional/keyword parameters are supported")

#     annotation = paramater.annotation
#     if annotation == inspect.Parameter.empty:
#         lambda node: node.args.value if issubclass(
#             node.args, ValueArgs
#         ) else NotImplemented

#     # Node
#     if annotation == Node:
#         return lambda node: node

#     # Node[SomeArgType]
#     if issubclass(parameter, Node):
#         return (
#             lambda node: node
#             if isinstance(node.args, get_inner(parameter))
#             else NotImplemented
#         )
#     # int
#     return (
#         lambda node: node.args.value
#         if issubclass(node.args, ValueArgs) and issubclass(node.args.value, parameter)
#         else NotImplemented
#     )
