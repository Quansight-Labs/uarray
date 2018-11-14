import numpy as np

from .moa import *


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
def BroadcastShapes(
    l: CVectorCallable[CArray], r: CVectorCallable[CArray]
) -> CVectorCallable[CArray]:
    """
    Returns unified shape of two input shapes
    https://docs.scipy.org/doc/numpy-1.15.1/reference/ufuncs.html#broadcasting
    """
    ...


register(
    BroadcastShapes(VectorCallable(), VectorCallable(ws("rs"))),
    lambda rs: VectorCallable(*rs),
)
register(
    BroadcastShapes(VectorCallable(ws("ls")), VectorCallable()),
    lambda ls: VectorCallable(*ls),
)


def _broadcast_shapes(
    ls: typing.Sequence[CArray], l: CInt, rs: typing.Sequence[CArray], r: CInt
) -> CVectorCallable[CArray]:
    l_, r_ = l.name, r.name
    if l_ == 1 or r_ == 1 or l_ == r_:
        d_ = max(l_, r_)
    else:
        raise ValueError(f"Cannot broadcast dimensions {l_} and {r_}")
    return ConcatVectorCallable(
        BroadcastShapes(VectorCallable(*ls), VectorCallable(*rs)),
        VectorCallable(Scalar(Int(d_))),
    )


register(
    BroadcastShapes(
        VectorCallable(ws("ls"), Scalar(sw("l", Int))),
        VectorCallable(ws("rs"), Scalar(sw("r", Int))),
    ),
    _broadcast_shapes,
)
