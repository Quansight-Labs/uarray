import inspect
import pprint

import matchpy

__all__ = ["replace", "w", "ws", "register", "replace_debug"]
replacer = matchpy.ManyToOneReplacer()
replace = replacer.replace


MAX_COUNT = 1000


@property
def _matchpy_reduce(self):
    replaced = True
    replace_count = 0
    while replaced and replace_count < MAX_COUNT:
        replaced = False
        for subexpr, pos in matchpy.expressions.functions.preorder_iter_with_position(
            self
        ):
            try:
                replacement, subst = next(iter(replacer.matcher.match(subexpr)))
                try:
                    result = replacement(**subst)
                except TypeError as e:
                    # TODO: set custom traceback with line number
                    # https://docs.python.org/3/library/traceback.html
                    # https://docs.python.org/3/library/inspect.html#inspect.getsource
                    raise TypeError(
                        f"Couldn't call {inspect.getsourcelines(replacement)} with {repr(subst)} when matching {repr(subexpr)}"
                    ) from e
                # TODO: Handle multiple return expressions
                if not isinstance(result, matchpy.Expression):
                    raise ValueError(
                        f"Replacement {replacement}({inspect.getsourcelines(replacement)}) should return an Expression instead of {result}"
                    )
                self = matchpy.functions.replace(self, pos, result)
                yield self
                replaced = True
                break
            except StopIteration:
                pass
        replace_count += 1


matchpy.Operation.r = _matchpy_reduce


class SymbolWildcardMaker:
    def __init__(self, symbol):
        self.symbol = symbol

    def __getattribute__(self, name):
        return matchpy.Wildcard.symbol(name, super().__getattribute__("symbol"))


class classproperty(object):
    """
    https://stackoverflow.com/a/5192374/907060
    """

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


matchpy.Symbol.w = classproperty(SymbolWildcardMaker)


class DotWildcardMaker:
    def __getattribute__(self, name):
        return matchpy.Wildcard.dot(name)


class StarWildcardMaker:
    def __getattribute__(self, name):
        return matchpy.Wildcard.star(name)


w = DotWildcardMaker()
ws = StarWildcardMaker()


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


pprint.PrettyPrinter._dispatch[matchpy.Operation.__repr__] = _pprint_operation

# defer ipython pretty printing to pprint
matchpy.Operation._repr_pretty_ = lambda self, pp, cycle: pp.text(pprint.pformat(self))


def replace_debug(expr, use_pprint=False, n=100):
    res = expr
    for _ in range(n):
        printer = pprint.pprint if use_pprint else print
        printer(res)
        new_res = replace(res, 1, print_steps=True)
        if new_res == res:
            break
        res = new_res
    return res


def register(*args):
    pattern, *constraints, replacement = args
    replacer.add(
        matchpy.ReplacementRule(matchpy.Pattern(pattern, *constraints), replacement)
    )
