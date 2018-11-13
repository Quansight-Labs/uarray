import logging

import matchpy
import numpy as np
from IPython.display import display

from .moa import *

logger = logging.getLogger(__name__)


class IPythonHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        display({record.msg: record.args})


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
        sw("fn", BinaryUfunc),
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


@operation
def BroadcastToShape(arr: CArray, shape: CVectorCallable) -> CArray:
    """
    Returns broadcasted values of args
    https://docs.scipy.org/doc/numpy-1.15.1/reference/ufuncs.html#broadcasting
    """
    ...


register(BroadcastToShape(w("arr"), VectorCallable()), lambda arr: arr)
register(
    BroadcastToShape(
        Scalar(w("content")), VectorCallable(Scalar(w("outer_dim")), ws("rest_dims"))
    ),
    lambda content, outer_dim, rest_dims: Sequence(
        outer_dim,
        unary_function(
            lambda idx: BroadcastToShape(Scalar(content), VectorCallable(*rest_dims))
        ),
    ),
)

register(
    BroadcastToShape(
        Sequence(sw("length", Int), w("cont")),
        VectorCallable(Scalar(sw("outer_dim", Int)), ws("rest_dims")),
    ),
    lambda length, cont, outer_dim, rest_dims: Sequence(
        outer_dim,
        unary_function(
            lambda idx: BroadcastToShape(
                CallUnary(cont, idx), VectorCallable(*rest_dims)
            )
        ),
    ),
    matchpy.CustomConstraint(
        lambda outer_dim, length: outer_dim.name == length.name or length.name == 1
    ),
)
