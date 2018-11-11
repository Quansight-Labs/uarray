import inspect
import pprint
import typing
import matchpy


replacer = matchpy.ManyToOneReplacer()
replace = replacer.replace

w = matchpy.Wildcard.dot
ws = matchpy.Wildcard.star
sw = matchpy.Wildcard.symbol


def _matches(expr):
    for subexpr, pos in matchpy.expressions.functions.preorder_iter_with_position(expr):
        try:
            replacement, subst = next(iter(replacer.matcher.match(subexpr)))
        except StopIteration:
            continue
        yield pos, replacement, subst


def _replace_once(expr):
    pos, replacement, subst = next(iter(_matches(expr)))
    try:
        result = replacement(**subst)
    except TypeError as e:
        # TODO: set custom traceback with line number
        # https://docs.python.org/3/library/traceback.html
        # https://docs.python.org/3/library/inspect.html#inspect.getsource
        raise TypeError(
            f"Couldn't call {inspect.getsourcelines(replacement)} when matching {repr(e)}"
        ) from e

    return matchpy.functions.replace(expr, pos, result)


def replace_scan(expr: matchpy.Expression) -> matchpy.Expression:
    while True:
        yield expr
        expr = _replace_once(expr)


def _pprint_operation(self, object, stream, indent, allowance, context, level):
    """
    Modified from pprint dict https://github.com/python/cpython/blob/3.7/Lib/pprint.py#L194
    """
    operands = object.operands
    if not operands:
        stream.write(repr(object))
        return
    cls = object.__class__
    stream.write(cls.__name__ + "(")
    self._format_items(
        operands, stream, indent + len(cls.__name__), allowance + 1, context, level
    )
    stream.write(")")


pprint.PrettyPrinter._dispatch[  # type: ignore
    matchpy.Operation.__repr__
] = _pprint_operation
# defer ipython pretty printing to pprint
matchpy.Operation._repr_pretty_ = lambda self, pp, cycle: pp.text(pprint.pformat(self))

T = typing.TypeVar("T")


# fallback when we haven't defined typing for operation
@typing.overload
def register(
    pattern: matchpy.Operation,
    replacement: typing.Callable,
    *constraints: matchpy.Constraint,
) -> None:
    ...


# we require replacement to return same category type of original expression
@typing.overload
def register(
    pattern: T, replacement: typing.Callable[..., T], *constraints: matchpy.Constraint
) -> None:
    ...


def register(
    pattern: T, replacement: typing.Callable[..., T], *constraints: matchpy.Constraint
) -> None:
    replacer.add(
        matchpy.ReplacementRule(matchpy.Pattern(pattern, *constraints), replacement)
    )


# def register_decorator(fn: typing.Callable[..., typing.Tuple[V, V]]) -> None:
#     """
#     Turn this


#     into this

#         w_length: CContent = w("length")
#         w_getitem: CGetitem = w("getitem")


#         def _getitem_sequence(length: CContent, getitem: CGetitem) -> CGetitem:
#             return getitem


#         register(GetItem(Sequence(w_length, w_getitem)), _getitem_sequence)
#     """
#     sig = inspect.signature(fn)

#     pass


CALLABLE = typing.TypeVar("CALLABLE", bound=typing.Callable)


@typing.overload
def operation(fn: CALLABLE) -> CALLABLE:
    ...


@typing.overload
def operation(
    *, to_str: typing.Callable[..., str] = None, name: str = None, infix: bool = False
) -> typing.Callable[[CALLABLE], CALLABLE]:
    ...


def operation(
    fn: CALLABLE = None,
    *,
    to_str: typing.Callable[..., str] = None,
    name: str = None,
    infix: bool = False,
) -> typing.Union[typing.Callable[[CALLABLE], CALLABLE], CALLABLE]:
    """
    Register a matchpy operation for a function.

    The function should have a fixed number of args and one return.

    This can also be done manually, by typing the result of `matchpy.Operation.new`
    as a callable, but this is more fluent.

    Manual way is like this:

        Sequence: t.Callable[[CContent, CGetitem], CArray] = mp.Operation.new(
            "Sequence", mp.Arity.binary
        )
    """

    def inner(fn: CALLABLE) -> CALLABLE:
        sig = inspect.signature(fn)

        min_operands = 0
        fixed = True
        names: typing.List[str] = []
        for p in sig.parameters.values():
            names.append(p.name)
            # *xs
            if p.kind == p.VAR_POSITIONAL:
                fixed = False
            # x
            elif p.kind == p.POSITIONAL_OR_KEYWORD:
                min_operands += 1
            elif p.kind == p.KEYWORD_ONLY:
                if p.name is not "variable_name":
                    raise ValueError(
                        f"Keyword only arg must be variable_name not {p.name}"
                    )

            else:
                raise NotImplementedError(f"Can't infer operation from paramater {p}")
        op = matchpy.Operation.new(
            name or fn.__name__,
            matchpy.Arity(min_operands, fixed),
            class_name=fn.__name__,
            infix=infix,
        )
        if to_str is not None:
            op.__str__ = lambda self, names=names: to_str(
                **{d: val for d, val in zip(names, self.operands)}
            )
        return typing.cast(CALLABLE, op)

    if fn is not None:
        return inner(fn)
    return inner


def new_symbol(name):
    symb = type(name, (matchpy.Symbol,), {})
    symb.__str__ = lambda self: str(self.name)
    return symb


V = typing.TypeVar("V")


def symbol(fn: typing.Callable[[T], V]) -> typing.Callable[[T], V]:
    return new_symbol(fn.__name__)
