import collections
import inspect
import typing

import matchpy


_CALLABLE = typing.TypeVar("_CALLABLE", bound=typing.Callable)

_T = typing.TypeVar("_T")


Pair = typing.Tuple[typing.Callable[[], _T], typing.Callable[[], _T]]


class NoMatchesException(RuntimeError):
    pass


class ManyToOneReplacer(matchpy.ManyToOneReplacer):
    def _first_match(self, expr):
        for subexpr, pos in matchpy.expressions.functions.preorder_iter_with_position(
            expr
        ):
            try:
                replacement, subst = next(iter(self.matcher.match(subexpr)))
            except StopIteration:
                continue
            return pos, replacement, subst
        raise NoMatchesException()

    def _replace_once(self, expr):
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
            return matchpy.functions.replace(expr, pos, result)
        except ValueError as e:
            raise ValueError(
                f"Failed to replace using {repr(replacement)} giving {repr(result)}"
            ) from e

    def replace_scan(self, expr: matchpy.Expression) -> matchpy.Expression:
        while True:
            yield expr
            try:
                expr = self._replace_once(expr)
            except NoMatchesException:
                return

    def replacement(self, fn: typing.Callable[..., Pair[_T]]) -> None:
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
            is_symbol, symbol_type = is_symbol_type(p.annotation)
            if not is_sequence and not is_symbol:
                wildcards.append(matchpy.Wildcard.dot(p.name))
            elif is_sequence and not is_symbol:
                wildcards.append([matchpy.Wildcard.star(p.name)])
            elif not is_sequence and is_symbol:
                wildcards.append(matchpy.Wildcard.symbol(p.name, symbol_type))
            else:
                raise NotImplementedError()
                # wildcards.append([ws(p.name)])
                # def custom_constraint(symbols):
                #     return all(isinstance(s, p.annotation) for s in symbols)

                # constraints.append(matchpy.CustomConstraint(custom_constraint))
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


replacer = ManyToOneReplacer()
replace = replacer.replace
replace_scan = replacer.replace_scan
replacement = replacer.replacement


@typing.overload
def operation(fn: _CALLABLE) -> _CALLABLE:
    ...


@typing.overload
def operation(
    *, to_str: typing.Callable[..., str] = None, name: str = None, infix: bool = False
) -> typing.Callable[[_CALLABLE], _CALLABLE]:
    ...


def operation(
    fn: _CALLABLE = None,
    *,
    to_str: typing.Callable[..., str] = None,
    name: str = None,
    infix: bool = False,
) -> typing.Union[typing.Callable[[_CALLABLE], _CALLABLE], _CALLABLE]:
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

    def inner(fn: _CALLABLE) -> _CALLABLE:
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
                **{
                    d: val
                    for d, val in zip(names, self.operands + [self.variable_name])
                }
            )
        return typing.cast(_CALLABLE, op)

    if fn is not None:
        return inner(fn)
    return inner


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


def is_symbol_type(t: typing.Any) -> typing.Tuple[bool, typing.Optional[typing.Type]]:
    """
    Returns whether the type, extracted from function signature, is a `matchpy.Symbol`
    subclass.
    """
    if isinstance(t, typing._GenericAlias):  # type: ignore
        t = t.__origin__
    if not isinstance(t, type):
        return False, None
    return issubclass(t, matchpy.Symbol), t


class Symbol(matchpy.Symbol, typing.Generic[_T]):
    def __init__(self, name: _T, variable_name=None):
        super().__init__(name, variable_name)

    def value(self) -> _T:
        return self.name

    def __str__(self):
        return str(self.name)
