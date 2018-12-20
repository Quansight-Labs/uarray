import collections
import inspect
import typing

import matchpy

__all__ = [
    "DoubleThunkType",
    "replace",
    "replace_scan",
    "operation",
    "Symbol",
    "replacement",
    "operation_and_replacement",
]
T = typing.TypeVar("T")


T_callable = typing.TypeVar("T_callable", bound=typing.Callable)

DoubleThunkType = typing.Tuple[typing.Callable[[], T], typing.Callable[[], T]]


class _NoMatchesException(RuntimeError):
    pass


class ManyToOneReplacer(matchpy.ManyToOneReplacer):
    def _first_match(self, expr: matchpy.Expression):
        for (
            subexpr,
            pos,
        ) in matchpy.expressions.functions.preorder_iter_with_position(  # type: ignore
            expr
        ):
            try:
                replacement, subst = next(iter(self.matcher.match(subexpr)))
            except StopIteration:
                continue
            return pos, replacement, subst
        raise _NoMatchesException()

    def _replace_once(self, expr: matchpy.Expression) -> matchpy.Expression:
        pos, replacement, subst = self._first_match(expr)
        try:
            result = replacement(**subst)
        except TypeError as e:
            # TODO: set custom traceback with line number
            # https://docs.python.org/3/library/traceback.html
            # https://docs.python.org/3/library/inspect.html#inspect.getsource
            raise TypeError(
                f"Couldn't call {inspect.getsourcelines(replacement)} when matching {repr(e)}"
            ) from e
        try:
            return matchpy.functions.replace(expr, pos, result)  # type: ignore
        except ValueError as e:
            raise ValueError(
                f"Failed to replace using {repr(replacement)} giving {repr(result)}"
            ) from e

    def replace_scan(
        self, expr: matchpy.Expression
    ) -> typing.Iterator[matchpy.Expression]:
        while True:
            yield expr
            try:
                expr = self._replace_once(expr)
            except _NoMatchesException:
                return

    def replacement(self, fn: typing.Callable[..., DoubleThunkType[T]]) -> None:
        """
        Uses a function to register a replacement rule. The function should take
        in all "holes" that we want to match on and return two lambdas. The first is the
        expression to match against. The second is the value it should be replaced with.
        """
        sig = inspect.signature(fn)

        wildcards: typing.List[
            typing.Union[matchpy.Wildcard, typing.Sequence[matchpy.Wildcard]]
        ] = []
        constraints: typing.List[matchpy.Constraint] = []
        for p in sig.parameters.values():
            is_sequence = is_sequence_type(p.annotation)
            symbol_type = is_symbol_type(p.annotation)
            if not is_sequence and not symbol_type:
                wildcards.append(matchpy.Wildcard.dot(p.name))
            elif is_sequence and not symbol_type:
                wildcards.append([matchpy.Wildcard.star(p.name)])
            elif not is_sequence and symbol_type:
                if hasattr(symbol_type, "constraint"):
                    constraint = symbol_type.constraint  # type: ignore
                    constraints.append(constraint)
                    symbol_type = symbol_type.__bases__[0]
                wildcards.append(matchpy.Wildcard.symbol(p.name, symbol_type))
            else:
                raise NotImplementedError()
            if p.kind != p.POSITIONAL_OR_KEYWORD:
                raise NotImplementedError(f"Can't infer replacement from paramater {p}")
        pattern = fn(*wildcards)[0]()

        def replacement_fn(**kwargs):
            return fn(**kwargs)[1]()

        self.add(
            matchpy.ReplacementRule(
                matchpy.Pattern(pattern, *constraints), replacement_fn
            )
        )

    def operation_and_replacement(self, fn: T_callable) -> T_callable:
        op = operation(fn)
        self.add(
            matchpy.ReplacementRule(
                matchpy.Pattern(op(matchpy.Wildcard.star("args"))),
                lambda args: fn(*args),
            )
        )
        return op


replacer = ManyToOneReplacer()
replace = replacer.replace
replace_scan = replacer.replace_scan
replacement = replacer.replacement
operation_and_replacement = replacer.operation_and_replacement


class Arg(typing.NamedTuple):
    name: str
    is_star: bool


def _analyze_args(params: typing.Sequence[inspect.Parameter]) -> typing.Iterable[Arg]:
    for p in params:
        # *xs
        if p.kind == p.VAR_POSITIONAL:
            is_star = True
        # x
        elif p.kind == p.POSITIONAL_OR_KEYWORD:
            is_star = False
        else:
            raise NotImplementedError(f"Can't infer operation from paramater {p}")
        yield Arg(p.name, is_star)


def _arity_from_args(args: typing.Iterable[Arg]) -> matchpy.Arity:
    return matchpy.Arity(
        len([None for a in args if not a.is_star]),
        not any(map(lambda a: a.is_star, args)),
    )


def operation(fn: T_callable) -> T_callable:
    """
    Register a matchpy operation for a function.

    The function should have a fixed number of args and one return.

    This can also be done manually, by typing the result of `matchpy.Operation.new`
    as a callable, but this is more fluent.

    Manual way is like this:

        Sequence: t.Callable[[CContent, CGetItem], ArrayType] = mp.Operation.new(
            "Sequence", mp.Arity.binary
        )
    """

    args = list(_analyze_args(list(inspect.signature(fn).parameters.values())))
    op = matchpy.Operation.new(fn.__name__, _arity_from_args(args))
    op.args = args  # type: ignore
    return typing.cast(T_callable, op)


def is_sequence_type(t: typing.Any) -> bool:
    """
    Returns whether the type, extracted from function signature, is a `typing.Sequence`
    subtype.

    This is hacky, would appreciate better way if found!

    https://stackoverflow.com/a/50103907/907060
    """
    try:
        return t.__origin__ is collections.abc.Sequence
    except AttributeError:
        return False


def is_symbol_type(t: typing.Any) -> typing.Optional[typing.Type[matchpy.Symbol]]:
    """
    Returns the symbol type extracted from the type signature, if it is one.
    """
    if isinstance(t, typing._GenericAlias):  # type: ignore
        t = t.__origin__
    if not isinstance(t, type) or not issubclass(t, matchpy.Symbol):
        return None
    return t


class Symbol(matchpy.Symbol, typing.Generic[T]):
    def __init__(self, name: T, variable_name=None):
        super().__init__(name, variable_name=None)

    def value(self) -> T:
        return self.name

    def __str__(self):
        return str(self.name)
