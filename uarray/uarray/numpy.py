import functools
import typing
import pprint
import itertools
import logging
from IPython.display import display


import numpy as np

from .moa import *


logger = logging.getLogger(__name__)


class IPythonHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        display(record.args)


logger.addHandler(IPythonHandler())


def _fn_string(fn):
    if isinstance(fn, np.ufunc):
        return f"ufunc:{fn.__name__}"
    return f"{fn.__module__}.{fn.__name__}"


class Ufunc(matchpy.Symbol):
    def __init__(self, ufunc: np.ufunc, variable_name=None) -> None:
        super().__init__(ufunc, variable_name)

    def __str__(self):
        return f"np.{self.name.__name__}"


# On scalars, execute
register(Call(Ufunc(np.add), Scalar(w.l), Scalar(w.r)), lambda l, r: Scalar(Add(l, r)))
register(
    Call(Ufunc(np.multiply), Scalar(w.l), Scalar(w.r)),
    lambda l, r: Scalar(Multiply(l, r)),
)

# On sequences, forward
register(
    Call(Ufunc.w.fn, Sequence(w.length, w.content)),
    lambda fn, length, content: Sequence(
        length, function(1, lambda idx: Call(fn, Call(content, idx)))
    ),
)
register(
    Call(
        Ufunc.w.fn, Sequence(w.l_length, w.l_content), Sequence(w.r_length, w.r_content)
    ),
    lambda fn, l_length, l_content, r_length, r_content: Sequence(
        Unify(l_length, r_length),
        function(1, lambda idx: Call(fn, Call(l_content, idx), Call(r_content, idx))),
    ),
)


class Broadcast(matchpy.Operation):
    """
    Broadcast(arg1, arg2)

    Returns broadcasted values of args
    https://docs.scipy.org/doc/numpy-1.15.1/reference/ufuncs.html#broadcasting
    """

    name = "Broadcast"
    arity = matchpy.Arity(2, False)


# both scalars
register(Broadcast(Scalar(w.l), Scalar(w.r)), lambda l, r: (Scalar(l), Scalar(r)))
# one scalar
register(
    Broadcast(Sequence(w.l_length, w.l_content), Scalar(w.r)),
    lambda l_length, l_content, r: (
        Sequence(l_length, l_content),
        Sequence(l_length, function(1, lambda idx: Scalar(r))),
    ),
)
register(
    Broadcast(Scalar(w.l), Sequence(w.r_length, w.r_content)),
    lambda r_length, r_content, l: (
        Sequence(r_length, function(1, lambda idx: Scalar(l))),
        Sequence(r_length, r_content),
    ),
)
# length of 1
register(
    Broadcast(
        Sequence(Value.w.l_length, w.l_content), Sequence(Value.w.r_length, w.r_content)
    ),
    matchpy.CustomConstraint(lambda l_length: l_length.value == 1),
    lambda l_length, l_content, r_length, r_content: (
        Sequence(r_length, function(1, lambda idx: Call(Scalar(0), l_content))),
        Sequence(r_length, r_content),
    ),
)
register(
    Broadcast(
        Sequence(Value.w.l_length, w.l_content), Sequence(Value.w.r_length, w.r_content)
    ),
    matchpy.CustomConstraint(lambda r_length: r_length.value == 1),
    lambda l_length, l_content, r_length, r_content: (
        Sequence(l_length, l_content),
        Sequence(l_length, function(1, lambda idx: Call(Scalar(0), r_content))),
    ),
)
# same lengths
register(
    Broadcast(
        Sequence(Value.w.l_length, w.l_content), Sequence(Value.w.r_length, w.r_content)
    ),
    matchpy.CustomConstraint(
        lambda l_length, r_length: r_length.value == l_length.value
    ),
    lambda l_length, l_content, r_length, r_content: (
        Sequence(l_length, l_content),
        Sequence(l_length, r_content),
    ),
)


# class NumpyNDArray(matchpy.Symbol):
#     def __init__(self, value: np.ndarray) -> None:
#         self.value = value
#         super().__init__(repr(value))

#     def __str__(self):
#         return str(self.value)


# @to_expression.register(np.ndarray)
# def to_expression__nparray(v):
#     """
#     Turns a NumPy array into nested sequences
#     """

#     def unbound_inner(x, i):
#         if i == v.ndim:
#             return Scalar(Content(x))
#         return Sequence(
#             Value(v.shape[i]),
#             function(1, lambda idx: unbound_inner(Call(GetItem(x), idx), i + 1)),
#         )

#     return unbound_inner(NumpyNDArray(v), 0)
