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


class NumpyNDArray(matchpy.Symbol):
    def __init__(self, value: np.ndarray) -> None:
        self.value = value
        super().__init__(repr(value))

    def __str__(self):
        return str(self.value)


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


@functools.singledispatch
def to_expression(v) -> matchpy.Expression:
    """
    Convert some value into a matchpy expression
    """
    return scalar(v)


@to_expression.register(matchpy.Expression)
def to_expression__expr(v):
    return v


@to_expression.register(np.ndarray)
def to_expression__nparray(v):
    """
    Turns a NumPy array into nested sequences
    """

    def unbound_inner(x, i):
        if i == v.ndim:
            return Scalar(Content(x))
        return Sequence(
            Value(v.shape[i]),
            function(1, lambda idx: unbound_inner(Call(Content(x), idx), i + 1)),
        )

    return unbound_inner(NumpyNDArray(v), 0)


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


class ArrayLike(np.lib.mixins.NDArrayOperatorsMixin):
    def __init__(self, value) -> None:
        self.expr = to_expression(value)

    def __repr__(self):
        return f"ArrayLike({repr(self.expr)})"

    def __str__(self):
        return f"ArrayLike({str(self.expr)})"

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
        return ArrayLike(expr)

    def __getitem__(self, i):
        if not isinstance(i, tuple):
            i = (i,)
        expr = Index(vector_of(*map(Content, map(to_expression, i))), self.expr)
        return ArrayLike(expr)

    @property
    def replaced(self):
        return ArrayLike(replace(self.expr))


@to_expression.register(ArrayLike)
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


pprint.PrettyPrinter._dispatch[ArrayLike.__repr__] = _pprint_array_like


@functools.singledispatch
def from_expression(v):
    raise NotImplementedError(f"Cannot turn {repr(v)} into Python value")


@from_expression.register(Value)
def from_expression__value(v):
    return v.value


def to_nested(expr: matchpy.Expression):
    content = replace(Content(expr))
    if isinstance(content, Value):
        return content.value
    length = from_expression(replace(Length(expr)))
    return [to_nested(Call(content, Value(i))) for i in range(length)]


def to_numpy(expr: matchpy.Expression):
    """
    Gets a numpy array from a matchpy expression.

    It first evalutes shape of the expression and creates an empty
    numpy array.

    It then iterates through the possible indexes and fills in the array.

    TODO: Switch from executing code to generating AST.
    """
    n_dim_expr = replace(Dim(expr))
    logger.info("n_dim_expr %s", n_dim_expr)
    n_dim = from_expression(replace(n_dim_expr))
    logger.info("n_dim %s", n_dim)

    shape_i = gensym()
    unbound_shape = replace(Content(Index(vector_of(Unbound(shape_i)), Shape(expr))))
    logger.info("shape(expr) %s", unbound_shape)
    shape = [
        from_expression(replace(matchpy.substitute(unbound_shape, {shape_i: Value(i)})))
        for i in range(n_dim)
    ]
    logger.info("shape %s", shape)
    res = np.empty(shape)
    idx_names = [gensym() for _ in range(n_dim)]
    unbound_indexed = replace(Content(Index(vector_of(*map(Unbound, idx_names)), expr)))
    logger.info("indexed(expr) = %s", unbound_indexed)

    for indexes in itertools.product(*map(range, shape)):
        res[tuple(indexes)] = from_expression(
            replace(
                matchpy.substitute(
                    unbound_indexed,
                    {name: Value(idx) for name, idx in zip(idx_names, indexes)},
                )
            )
        )
    return res


def _index_ndarray(x: NumpyNDArray, idx: Value):
    res = x.value[idx.value]
    return NumpyNDArray(res) if isinstance(res, np.ndarray) else Scalar(Value(res))


register(Call(Content(NumpyNDArray.w.x), Value.w.idx), _index_ndarray)


class Optimized:
    def __init__(
        self,
        fn: typing.Callable[..., ArrayLike],
        final_call: typing.Callable[[matchpy.Expression], typing.Any] = to_numpy,
    ) -> None:
        self.fn = fn
        self.final_call = final_call
        functools.wraps(fn)(self)

    def __call__(self, *args, **kwargs):
        wrapped_args = [ArrayLike(a) for a in args]
        wrapped_kwargs = {k: ArrayLike(v) for k, v in kwargs.items()}

        logger.info(f"Calling %s(*%s, **%s)", self.fn, wrapped_args, wrapped_kwargs)

        res = self.fn(*wrapped_args, **wrapped_kwargs).expr
        logger.info(f"Got %s", res)

        replaced_res = replace(res)
        logger.info(f"Replaced %s", replaced_res)

        return self.final_call(replaced_res)


def optimize(*args, **kwargs):
    """
    @optimize(final_call=to_numpy)
    def f()...

    or

    @optimize
    def f():

    or

    optimize(f, final_call=to_numpy)

    or

    optimize(f, to_numpy)
    """
    if args:
        return Optimized(*args, **kwargs)
    return functools.partial(Optimized, **kwargs)
