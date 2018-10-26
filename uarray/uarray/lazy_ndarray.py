import numpy as np
import pprint
import logging

from .moa import *
from .core import *
from .numpy import *
from .ast import ToSequenceWithDim

logger = logging.getLogger(__name__)


class LazyNDArray(np.lib.mixins.NDArrayOperatorsMixin):
    def __init__(self, value) -> None:
        self.expr = to_expression(value)

    def __repr__(self):
        return f"LazyNDArray({repr(self.expr)})"

    def __str__(self):
        return f"LazyNDArray({str(self.expr)})"

    def _repr_pretty_(self, pp, cycle):
        return pp.text(pprint.pformat(self))

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        logger.info("__array_ufunc__(%s, %s, *%s, **%s)", ufunc, method, inputs, kwargs)

        if kwargs or len(inputs) not in (1, 2):
            return NotImplemented
        args = list(map(to_expression, inputs))
        logger.info("args = %s", args)
        fn = Ufunc(ufunc)
        if method == "__call__":
            if len(inputs) == 2:
                args = [Broadcast(*args)]
                logger.info("args = %s", args)
            expr = Call(fn, *args)
        elif method == "outer":
            expr = OuterProduct(
                function(2, lambda l, r: Content(Call(fn, Scalar(l), Scalar(r)))), *args
            )
        else:
            return NotImplemented
        logger.info("expr = %s", expr)
        return LazyNDArray(expr)

    def __getitem__(self, i):
        if not isinstance(i, tuple):
            i = (i,)
        expr = Index(vector_of(*map(Content, map(to_expression, i))), self.expr)
        return LazyNDArray(expr)

    def has_dim(self, d: int):
        return LazyNDArray(ToSequenceWithDim(self.expr, Value(d)))


@to_expression.register(LazyNDArray)
def to_expression__array_like(v):
    return v.expr


def _pprint_array_like(self, object_, stream, indent, allowance, context, level):
    """
    Modified from pprint dict https://github.com/python/cpython/blob/3.7/Lib/pprint.py#L194
    """

    cls = object_.__class__
    stream.write(cls.__name__ + "(")
    self._format(
        object_.expr,
        stream,
        indent + len(cls.__name__) + 1,
        allowance + 1,
        context,
        level,
    )
    stream.write(")")


pprint.PrettyPrinter._dispatch[LazyNDArray.__repr__] = _pprint_array_like
