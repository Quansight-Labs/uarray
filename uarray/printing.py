import functools
import inspect

import black
import matchpy
import matchpy.expressions.expressions

import numpy

# @functools.singledispatch
# def to_str(v):
#     return str(v)


@functools.singledispatch
def to_repr(v):
    return repr(v)


MAX_LINE_LENGTH = 120


def to_repr_black(o):
    return black.format_str(to_repr(o), line_length=MAX_LINE_LENGTH)


def repr_pretty(self, pp, cycle):
    return pp.text(to_repr_black(self))


def repr_(self):
    return to_repr(self)


matchpy.Operation._repr_pretty_ = repr_pretty
matchpy.Symbol._repr_pretty_ = repr_pretty

matchpy.Operation.__repr__ = repr_
matchpy.Symbol.__repr__ = repr_


@to_repr.register(list)
def to_repr_list(l):
    items = ", ".join(map(to_repr, l))
    return f"[{items}]"


@to_repr.register(dict)
def to_repr_dict(d):
    items = ", ".join(f"{to_repr(k)}: {to_repr(v)}" for k, v in d.items())
    return "{" + items + "}"


@to_repr.register(matchpy.Operation)
def to_repr_op(op: matchpy.Operation):
    args = list(map(to_repr, op.operands))
    if op.variable_name is not None:
        args.append(f"variable_name={to_repr(op.variable_name)}")
    return f"{type(op).__name__}({', '.join(args)})"


@to_repr.register(matchpy.Symbol)
def to_repr_s(s: matchpy.Symbol):
    return f"{type(s).__name__}({to_repr(s.name)})"


def _fn():
    pass


@to_repr.register(type(_fn))
def to_repr_func(f):
    nonlocals = to_repr(inspect.getclosurevars(f).nonlocals)
    return f"fn({repr(repr(f)[len('<function '):-1])}, {nonlocals})"


@to_repr.register(numpy.ufunc)
def to_repr_ufunc(f):
    return f"np.ufunc({f.__name__})"


@to_repr.register(matchpy.expressions.expressions._OperationMeta)
def to_repr_operation(op):
    return op.name
