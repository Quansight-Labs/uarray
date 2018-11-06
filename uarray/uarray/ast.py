import ast
import functools
import typing

import matchpy

from .core import *
from .machinery import *
from .moa import Add, Multiply


def to_tuple(fn):
    """
    Makes a generator return a tuple
    """

    @functools.wraps(fn)
    def inner(*args, **kwargs):
        return tuple(fn(*args, **kwargs))

    return inner


unary = matchpy.Arity.unary
binary = matchpy.Arity.binary


def new_operation(name, arity):
    return matchpy.Operation.new(name, arity, name)


NPArray = new_operation("NPArray", unary)

PythonContent = new_operation("PythonContent", unary)

Initializer = new_operation("Initializer", unary)

register(Initializer(NPArray(w.init)), lambda init: init)
register(Initializer(PythonContent(w.init)), lambda init: init)


ToNPArray = new_operation("ToNPArray", binary)
ToPythonContent = new_operation("ToPythonContent", unary)


class ShouldAllocate(matchpy.Symbol):
    name: bool


register(ToNPArray(NPArray(w.x), ShouldAllocate.w.alloc), lambda x, alloc: NPArray(x))
register(ToPythonContent(PythonContent(w.x)), lambda x: PythonContent(x))

# Scalar numpy arrays are converted to scalars, not 0d array
register(
    ToNPArray(Scalar(w.content), w.init),
    lambda content, init: NPArray(Initializer(ToPythonContent(content))),
)


class Expression(matchpy.Symbol):
    """
    Can use this as an initializer
    """

    name: ast.Expression

    def __repr__(self):
        return f"Expression({ast.dump(self.name)})"


# TODO: Is this right? Or should this never be hit
register(ToPythonContent(Expression.w.exp), lambda exp: PythonContent(exp))


class Statement(matchpy.Symbol):
    """
    Returned by all initializer functions
    """

    name: ast.AST

    def __repr__(self):
        return f"Statement({ast.dump(self.name)})"


class Identifier(matchpy.Symbol):
    name: str
    _i = 0

    def __init__(self, name=None, variable_name=None):
        if not name:
            name = f"i_{Identifier._i}"
            Identifier._i += 1
        super().__init__(name, variable_name)


def np_array_from_id(array_id: Identifier):
    assert isinstance(array_id, Identifier)
    return NPArray(Expression(ast.Name(array_id.name, ast.Load())))


def python_content_from_id(array_id: Identifier):
    assert isinstance(array_id, Identifier)
    return PythonContent(Expression(ast.Name(array_id.name, ast.Load())))


def _assign_expresion(expr: Expression, id_: Identifier) -> Statement:
    assert isinstance(id_, Identifier)
    return Statement(ast.Assign([ast.Name(id_.name, ast.Store())], expr.name))


register(Call(Expression.w.expr, Identifier.w.id_), _assign_expresion)


def _value_as_python_content(val: Value):
    v = val.value
    if isinstance(v, (int, float)):
        e = ast.Num(v)
    else:
        raise TypeError(f"Cannot turn {v} into Python AST")
    return PythonContent(Expression(e))


register(ToPythonContent(Value.w.val), _value_as_python_content)

expressions = typing.Union[matchpy.Expression, typing.Tuple[matchpy.Expression, ...]]


class SubstituteIdentifier(matchpy.Symbol):
    name: typing.Callable[[Identifier], expressions]


register(
    Call(SubstituteIdentifier.w.fn, Identifier.w.id), lambda fn, id: fn.name(id.name)
)


class SubstituteStatements(matchpy.Symbol):
    name: typing.Callable[..., expressions]


def all_of_type(type_):
    return lambda args: all(isinstance(a, type_) for a in args)


register(
    Call(SubstituteStatements.w.fn, ws.args),
    matchpy.CustomConstraint(all_of_type(Statement)),
    lambda fn, args: fn.name(*(a.name for a in args)),
)


def statements_then_init(fn):
    """
    statements_then_init is called to wrap a function
    that yields a bunch of statements and then returns
    an initializer 
    """

    @SubstituteIdentifier
    @to_tuple
    def inner(id_: str):
        generator = fn()
        while True:
            try:
                yield next(generator)
            except StopIteration as exc:
                initializer = exc.value
                yield Call(initializer, Identifier(id_))
                return

    return inner


ShapeAsTuple = new_operation("ShapeAsTuple", unary)


def _shape_as_tuple__scalar(_):
    return Expression(ast.Tuple([], ast.Load()))


register(ShapeAsTuple(Scalar(w._)), _shape_as_tuple__scalar)


def _shape_as_tuple__sequence(length, getitem):

    inner_seq = Call(getitem, Unbound())

    @statements_then_init
    def inner():
        inner_shape_id = Identifier()
        yield Call(ShapeAsTuple(inner_seq), inner_shape_id)
        length_id = Identifier()
        yield Call(Initializer(ToPythonContent(length)), length_id)
        return Expression(
            ast.BinOp(
                ast.Tuple([ast.Name(length_id.name, ast.Load())], ast.Load()),
                ast.Add(),
                ast.Name(inner_shape_id.name, ast.Load()),
            )
        )

    return inner


register(ShapeAsTuple(Sequence(w.length, w.getitem)), _shape_as_tuple__sequence)


def _to_np_array_sequence(length, getitem, alloc: ShouldAllocate):
    @NPArray
    @SubstituteIdentifier
    @to_tuple
    def inner(array_id: str):
        assert isinstance(array_id, str)
        if alloc.name:

            # get shape
            shape_tuple_id = Identifier()
            yield Call(ShapeAsTuple(Sequence(length, getitem)), shape_tuple_id)
            # allocate array
            array = ast.Call(
                ast.Attribute(ast.Name("np", ast.Load()), "empty", ast.Load()),
                [ast.Name(shape_tuple_id.name, ast.Load())],
                [],
            )
            yield Statement(ast.Assign([ast.Name(array_id, ast.Store())], array))

        length_id = Identifier()
        yield Call(Initializer(ToPythonContent(length)), length_id)

        index_id = Identifier()
        result_id = Identifier()
        # result = getitem(i)
        initialize_result = Call(
            Initializer(
                ToNPArray(
                    Call(getitem, python_content_from_id(index_id)),
                    ShouldAllocate(False),
                )
            ),
            result_id,
        )
        # result = array[i]
        set_result = ast.Assign(
            [ast.Name(result_id.name, ast.Store())],
            ast.Subscript(
                ast.Name(array_id, ast.Load()),
                ast.Index(ast.Name(index_id.name, ast.Load())),
                ast.Load(),
            ),
        )

        # we have to assign twice, this is for scalar case previous is for sequence
        # need to look into this more
        # array[i] = result
        set_array = ast.Assign(
            [
                ast.Subscript(
                    ast.Name(array_id, ast.Load()),
                    ast.Index(ast.Name(index_id.name, ast.Load())),
                    ast.Store(),
                )
            ],
            ast.Name(result_id.name, ast.Load()),
        )
        # range(length)
        range_expr = ast.Call(
            ast.Name("range", ast.Load()), [ast.Name(length_id.name, ast.Load())], []
        )

        @SubstituteStatements
        def inner(*results_initializer):
            # for i in range(length):
            return Statement(
                ast.For(
                    ast.Name(index_id.name, ast.Store()),
                    range_expr,
                    [set_result, *results_initializer, set_array],
                    [],
                )
            )

        yield Call(inner, initialize_result)

    return inner


# Scalar numpy arrays are converted to scalars, not 0d array
register(
    ToNPArray(Sequence(w.length, w.getitem), ShouldAllocate.w.alloc),
    _to_np_array_sequence,
)


ToSequenceWithDim = new_operation("ToSequenceWithDim", binary)


def _np_array_to_sequence(arr: Expression, ndim: Value):
    def inner(e: matchpy.Expression, i: int):
        if i == ndim.value:
            return Scalar(Content(e))

        length = Expression(
            ast.Subscript(
                ast.Attribute(arr.name, "shape", ast.Load()),
                ast.Index(ast.Num(i)),
                ast.Load(),
            )
        )

        return Sequence(
            length, function(1, lambda idx: inner(Call(GetItem(e), idx), i + 1))
        )

    return inner(NPArray(arr), 0)


register(
    ToSequenceWithDim(NPArray(Expression.w.arr), Value.w.ndim), _np_array_to_sequence
)


def _nparray_getitem(array_init, idx):
    @NPArray
    @SubstituteIdentifier
    @to_tuple
    def inner(sub_array_id: str):
        idx_id = Identifier()
        yield Call(Initializer(ToPythonContent(idx)), idx_id)
        array_id = Identifier()
        yield Call(array_init, array_id)
        # sub_array = array[idx]
        yield Statement(
            ast.Assign(
                [ast.Name(sub_array_id, ast.Store())],
                ast.Subscript(
                    ast.Name(array_id.name, ast.Load()),
                    ast.Index(ast.Name(idx_id.name, ast.Load())),
                    ast.Load(),
                ),
            )
        )

    return inner


register(Call(GetItem(NPArray(w.array_init)), w.idx), _nparray_getitem)


# for now we just noop
# def _nparray_content(array_init):
#     # scalar =np.asscalar(array)
#     @PythonContent
#     @SubstituteIdentifier
#     @to_tuple
#     def inner(scalar_id: str):
#         array_id = Identifier()
#         yield Call(array_init, array_id)
#         yield Statement(
#             ast.Assign(
#                 [ast.Name(scalar_id, ast.Store())],
#                 ast.Call(
#                     ast.Attribute(ast.Name("np", ast.Load()), "asscalar", ast.Load()),
#                     [ast.Name(array_id.name, ast.Load())],
#                     [],
#                 ),
#             )
#         )

#     return inner


register(Content(NPArray(w.array_init)), lambda array_init: PythonContent(array_init))


def _multiply_python_content(l_init, r_init):
    # res = l * r
    @PythonContent
    @SubstituteIdentifier
    @to_tuple
    def inner(res_id: str):
        l_id = Identifier()
        r_id = Identifier()
        yield Call(l_init, l_id)
        yield Call(r_init, r_id)
        yield Statement(
            ast.Assign(
                [ast.Name(res_id, ast.Store())],
                ast.BinOp(
                    ast.Name(l_id.name, ast.Load()),
                    ast.Mult(),
                    ast.Name(r_id.name, ast.Load()),
                ),
            )
        )

    return inner


register(
    Multiply(PythonContent(w.l_init), PythonContent(w.r_init)), _multiply_python_content
)


def _add_python_content(l_init, r_init):
    # res = l + r
    @PythonContent
    @SubstituteIdentifier
    @to_tuple
    def inner(res_id: str):
        l_id = Identifier()
        r_id = Identifier()
        yield Call(l_init, l_id)
        yield Call(r_init, r_id)
        yield Statement(
            ast.Assign(
                [ast.Name(res_id, ast.Store())],
                ast.BinOp(
                    ast.Name(l_id.name, ast.Load()),
                    ast.Add(),
                    ast.Name(r_id.name, ast.Load()),
                ),
            )
        )

    return inner


register(Add(PythonContent(w.l_init), PythonContent(w.r_init)), _add_python_content)

register(Initializer(NPArray(w.init)), lambda init: init)


register(
    ToPythonContent(Add(w.x, w.y)),
    lambda x, y: Add(ToPythonContent(x), ToPythonContent(y)),
)
register(
    ToPythonContent(Multiply(w.x, w.y)),
    lambda x, y: Multiply(ToPythonContent(x), ToPythonContent(y)),
)

# def compile_function()


DefineFunction = new_operation("DefineFunction", matchpy.Arity(1, False))


def _define_function(ret, args):

    ret_id = Identifier()

    args_ = ast.arguments(
        args=[ast.arg(arg=a.name, annotation=None) for a in args],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
    )

    @SubstituteStatements
    def inner(*initialize_ret):
        return Statement(
            ast.Module(
                body=[
                    ast.FunctionDef(
                        name="fn",
                        args=args_,
                        body=[
                            *initialize_ret,
                            ast.Return(value=ast.Name(id=ret_id.name, ctx=ast.Load())),
                        ],
                        decorator_list=[],
                        returns=None,
                    )
                ]
            )
        )

    return Call(inner, Call(Initializer(ret), ret_id))


register(DefineFunction(w.ret, ws.args), _define_function)


def _vector_indexed_python_content(idx_expr: Expression, args: typing.List[Expression]):
    return PythonContent(
        Expression(
            ast.Subscript(
                value=ast.Tuple(elts=[a.name for a in args], ctx=ast.Load()),
                slice=ast.Index(value=idx_expr.name),
                ctx=ast.Load(),
            )
        )
    )

    # recurses forever
    # return ToPythonContent(
    #     Content(
    #         Call(GetItem(ToNestedLists(vector_of(*items))), PythonContent(idx_init))
    #     )
    # )


# TODO: Make work with non expressions
register(
    VectorIndexed(PythonContent(Expression.w.idx_expr), ws.args),
    matchpy.CustomConstraint(all_of_type(Expression)),
    _vector_indexed_python_content,
)
