import ast
import matchpy


from .numpy import *


class AssignAsNPArray(matchpy.Operation):
    """
    AssignAsNpArray(expr, id, allocate) -> statements that initialize identifier with NP array
    """

    arity = matchpy.Arity(3, True)


class AssignAsNestedList(matchpy.Operation):
    """
    AssignAsNestedList(expr, id) -> statements that initialize identifier with nested lists
    """

    arity = matchpy.Arity(2, True)


class AssignAsValue(matchpy.Operation):
    """
    AssignAsValue(expr, id) -> statement that initialize identifier with native python value

    (used on contents of scalar)
    """


_i = 0


def gen_id():
    global _i
    s = f"id{_i}"
    _i += 1
    return s


class SubstituteStatements(matchpy.Symbol):
    """
    SubstituteStatements(fn)
    """

    pass


register(
    Call(SubstituteStatements.w.fn, ws.args),
    matchpy.CustomConstraint(
        lambda args: all(isinstance(a, SubstituteStatements) for a in args)
    ),
    lambda fn, args: fn.name(*(a.name for a in args)),
)


def to_tuple(fn):
    """
    Makes a generator return a tuple
    """

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        return tuple(fn(*args, **kwargs))

    return inner


class Statement(matchpy.Symbol):
    def __repr__(self):
        return f"Statement({ast.dump(self.name)})"


class Expression(matchpy.Symbol):
    def __repr__(self):
        return f"Expression({ast.dump(self.name)})"


@to_tuple
def assign_sequence_nparray(length, content, id: Value, allocate: Value):
    if allocate.value:
        shape_list_id = gen_id()
        # fill shape
        yield AssignAsNestedList(Shape(Sequence(length, content)), Value(shape_list_id))
        # allocate array
        shape_tuple = ast.Call(
            ast.Name("tuple", ast.Load()), [ast.Name(shape_list_id, ast.Load())], []
        )
        array = ast.Call(
            ast.Attribute(ast.Name("np", ast.Load()), "array", ast.Load()),
            [shape_tuple],
            [],
        )
        yield Statement(ast.Assign([ast.Name(id.value, ast.Store())], array))
    index_id = gen_id()
    index = ast.Subscript(
        ast.Name(id.value, ast.Load()),
        ast.Index(ast.Name(index_id, ast.Load())),
        ast.Load(),
    )

    length_id = gen_id()
    indexed_id = gen_id()

    def inner(*length_assignments):
        @to_tuple
        def inner(*index_assignments):
            yield from length_assignments
            yield Statement(
                ast.For(
                    ast.Name(index_id, ast.Store()),
                    ast.Call(
                        ast.Name("range", ast.Load()),
                        [ast.Name(length_id, ast.Load())],
                        [],
                    ),
                    [
                        ast.Assign(
                            [ast.Name(indexed_id, ast.Store())],
                            ast.Subscript(
                                ast.Name(id.value, ast.Load()),
                                Index(ast.Name(index_id, ast.Load())),
                                ast.Load(),
                            ),
                        ),
                        *index_assignments,
                    ],
                )
            )

        return SubstituteStatements(inner)

    yield Call(
        Call(SubstituteStatements(inner), AssignAsValue(length, Value(length_id))),
        AssignAsNPArray(
            Call(content, Expression(index)), Value(indexed_id), Value(False)
        ),
    )


register(
    AssignAsNPArray(Sequence(w.length, w.content), Value.w.id, Value.w.allocate),
    assign_sequence_nparray,
)

# Scalar arrays should be values not 0d arrays to match NP behavior
register(
    AssignAsNPArray(Scalar(w.content), Value.w.id, Value.w.allocate),
    lambda content, id, allocate: AssignAsValue(content, id),
)


def _assign_value(v: Value, id: Value) -> Statement:
    v = v.value
    if isinstance(v, (int, float)):
        e = ast.Num(v)
    else:
        raise TypeError(f"Cannot turn {v} into Python AST")
    return Statement(ast.Assign([ast.Name(id.value, ast.Store())], e))


register(AssignAsValue(Value.w.x, Value.w.id), _assign_value)


def _assign_multiply(l, r, id):
    l_id = gen_id()
    r_id = gen_id()

    def inner(l_assignments):
        @to_tuple
        def inner(r_assignments):
            yield from l_assignments
            yield from r_assignments
            res = ast.BinOp(
                ast.Name(l_id, ast.Load()), ast.Mult(), ast.Name(r_id, ast.Load())
            )
            yield Statement(ast.Assign([ast.Name(id.value, ast.Store())], res))

        return inner

    return Call(
        Call(SubstituteStatements(inner), AssignAsValue(l, l_id)),
        AssignAsValue(r, r_id),
    )


register(AssignAsValue(Multiply(w.l, w.r), Value.w.id), _assign_multiply)


class NPArrayExpression(matchpy.Symbol):
    """
    Expression that holds a Numpy ND array.
    """

    pass


class ToSequenceWithDim(matchpy.Operation):
    name = "ToSequenceWithDim"
    arity = matchpy.Arity(2, True)


register(ToSequenceWithDim(Sequence(ws.args), w._), lambda args, _: Sequence(args))
register(ToSequenceWithDim(Sequence(ws.args), w._), lambda args: Sequence(args))


def np_array_with_ndim(a: matchpy.Expression, n_dim: int, i=0) -> Sequence | Scalar:
    """
    Takes in an expression can be turned into an ndarray assignment and expands it out
    as nested sequences, so that it can be reduced and understood.
    """
    a_id = gen_id()
    a_assignments = AssignAsNPArray(e, Value(a_id), Value(True))

    if i == n_dim:
        return Scalar(a)
    return Sequence(
        shape[i],
        function(1, lambda idx: with_shape(Call(Content(x), idx), shape, i + 1)),
    )
    shape_expr = ast.Attribute(ast.e, attr="shape", ctx=Load())
    with_shape(e)


# TODO: Make new class for input Numpy Args with dims that handles shape correctly as well
# as getting values correctly.
# class

# TODO: Makes decorator take in *args and wrapper arguments that passes them through, wrapping in ArrayLike

# def _index_expression(e, idx):
#     idx_id = gen_id()
#     @to_tuple
#     def inner(idx_assignments):
#         yield from idx_assignments


#     return Call(Substitute(inner), AssignAsValue(idx))


# register(Call(Content(Expression.w.e), w.idx), _index_expression)
