import logging

import matchpy
import numpy as np
from IPython.display import display

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


@symbol
def BinaryUfunc(ufunc: np.ufunc) -> CCallableBinary[CArray, CArray, CArray]:
    ...


# On scalars, execute
register(
    CallBinary(BinaryUfunc(np.add), Scalar(w("l")), Scalar(w("r"))),
    lambda l, r: Scalar(Add(l, r)),
)
register(
    CallBinary(BinaryUfunc(np.multiply), Scalar(w("l")), Scalar(w("r"))),
    lambda l, r: Scalar(Multiply(l, r)),
)

# On sequences, forward
register(
    CallBinary(
        sw(BinaryUfunc, "fn"),
        Sequence(w("l_length"), w("l_content")),
        Sequence(w("r_length"), w("r_content")),
    ),
    lambda fn, l_length, l_content, r_length, r_content: Sequence(
        Unify(l_length, r_length),
        unary_function(
            lambda idx: CallBinary(
                fn, CallUnary(l_content, idx), CallUnary(r_content, idx)
            )
        ),
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
register(Broadcast(Scalar(w("l")), Scalar(w("r"))), lambda l, r: (Scalar(l), Scalar(r)))
# one scalar
register(
    Broadcast(Sequence(w("l_length"), w("l_content")), Scalar(w("r"))),
    lambda l_length, l_content, r: (
        Sequence(l_length, l_content),
        Sequence(l_length, unary_function(lambda idx: Scalar(r))),
    ),
)
register(
    Broadcast(Scalar(w("l")), Sequence(w("r_length"), w("r_content"))),
    lambda r_length, r_content, l: (
        Sequence(r_length, unary_function(lambda idx: Scalar(l))),
        Sequence(r_length, r_content),
    ),
)
# length of 1
register(
    Broadcast(
        Sequence(sw(Int, "l_length"), w("l_content")),
        Sequence(sw(Int, "r_length"), w("r_content")),
    ),
    matchpy.CustomConstraint(lambda l_length: l_length.name == 1),
    lambda l_length, l_content, r_length, r_content: (
        Sequence(r_length, unary_function(lambda idx: CallUnary(l_content, Int(0)))),
        Sequence(r_length, r_content),
    ),
)
register(
    Broadcast(
        Sequence(sw(Int, "l_length"), w("l_content")),
        Sequence(sw(Int, "r_length"), w("r_content")),
    ),
    matchpy.CustomConstraint(lambda r_length: r_length.name == 1),
    lambda l_length, l_content, r_length, r_content: (
        Sequence(l_length, l_content),
        Sequence(l_length, unary_function(lambda idx: CallUnary(r_content, Int(0)))),
    ),
)
# same lengths
register(
    Broadcast(
        Sequence(sw(Int, "l_length"), w("l_content")),
        Sequence(sw(Int, "r_length"), w("r_content")),
    ),
    matchpy.CustomConstraint(lambda l_length, r_length: r_length.name == l_length.name),
    lambda l_length, l_content, r_length, r_content: (
        Sequence(l_length, l_content),
        Sequence(l_length, r_content),
    ),
)
