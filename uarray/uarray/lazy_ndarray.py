import typing

import numpy as np

from .ast import ToSequenceWithDim
from .logging import logger
from .numpy import *
from .printing import repr_pretty, to_repr


class LazyNDArray(np.lib.mixins.NDArrayOperatorsMixin):
    def __init__(self, value) -> None:
        self.expr = to_array(value)

    def __repr__(self):
        return f"LazyNDArray({repr(self.expr)})"

    def __str__(self):
        return f"LazyNDArray({str(self.expr)})"

    _repr_pretty_ = repr_pretty

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        logger.info("__array_ufunc__(%s, %s, *%s, **%s)", ufunc, method, inputs, kwargs)

        if kwargs or len(inputs) not in (1, 2):
            return NotImplemented
        args = list(map(to_array, inputs))
        logger.info("args = %s", args)
        fn = BinaryUfunc(ufunc)
        if method == "__call__":
            if len(args) == 2:
                broadcasted_shape = BroadcastShapes(
                    GetItem(Shape(args[0])), GetItem(Shape(args[1]))
                )
                args = [
                    BroadcastTo(args[0], Content(Dim(args[0])), broadcasted_shape),
                    BroadcastTo(args[1], Content(Dim(args[1])), broadcasted_shape),
                ]
                logger.info("args = %s", args)
            else:
                raise NotImplementedError("Only binary ufuncs supported")
            expr = CallBinary(fn, *args)
        elif method == "outer":
            expr = OuterProduct(fn, *args)
        else:
            return NotImplemented
        logger.info("expr = %s", expr)
        return LazyNDArray(expr)

    def __getitem__(self, i):
        if not isinstance(i, tuple):
            i = (i,)
        expr = Index(vector_of(*map(to_array, i)), self.expr)
        return LazyNDArray(expr)

    def reshape(self, new_shape, order="C"):
        if order != "C":
            raise NotImplementedError(f"cannot reshape to other order {order}")
        return LazyNDArray(Reshape(to_array(new_shape), self.expr))

    def has_dim(self, d: int):
        return LazyNDArray(ToSequenceWithDim(self.expr, Int(d)))

    def has_shape(self, shape: typing.Iterable[int]):
        return LazyNDArray(with_shape(self.expr, list(map(Int, shape))))


@to_array.register(LazyNDArray)
def to_expression__array_like(v):
    return v.expr


@to_repr.register(LazyNDArray)
def to_repr_lazyndarray(l):
    return f"{type(l).__name__}({to_repr(l.expr)})"
