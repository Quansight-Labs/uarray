import ast
import functools
import typing

import matchpy

from .ast_types import *
from .core import *
from .moa import Add, Multiply, Quotient, Remainder
from .printing import to_repr


def join_statements(
    fn: typing.Callable[[V], typing.Iterator[CStatements]]
) -> typing.Callable[[V], CStatements]:
    """
    Makes a generator return a tuple
    """

    @functools.wraps(fn)
    def inner(a: V) -> CStatements:
        s: CStatements = VectorCallable()
        for s_ in fn(a):
            s = ConcatVectorCallable(s, s_)
        return s

    return inner


unary = matchpy.Arity.unary
binary = matchpy.Arity.binary


@operation
def NPArray(init: CInitializer) -> CInitializableArray:
    ...


@operation
def PythonContent(init: CInitializer) -> CInitializableContent:
    ...


@operation
def Initializer(initializable: CInitializable) -> CInitializer:
    ...


register(Initializer(NPArray(w("init"))), lambda init: init)
register(Initializer(PythonContent(w("init"))), lambda init: init)


@operation
def ToPythonContent(content: CContent) -> CInitializableContent:
    ...


class ShouldAllocate(matchpy.Symbol):
    name: bool


@operation
def ToNPArray(arr: CArray, alloc: ShouldAllocate) -> CInitializableArray:
    ...


register(
    ToNPArray(NPArray(w("x")), sw("alloc", ShouldAllocate)), lambda x, alloc: NPArray(x)
)
register(ToPythonContent(PythonContent(w("x"))), lambda x: PythonContent(x))

# Scalar numpy arrays are converted to scalars, not 0d array
register(
    ToNPArray(Scalar(w("content")), w("init")),
    lambda content, init: NPArray(Initializer(ToPythonContent(content))),
)


@to_repr.register(ast.AST)
def to_repr_func(a):
    return f"{type(a).__name__}({ast.dump(a, annotate_fields=False)})"


@symbol
def Expression(name: ast.AST) -> CExpression:
    ...


# TODO: Is this right? Or should this never be hit
register(ToPythonContent(sw("exp", Expression)), lambda exp: PythonContent(exp))


@symbol
def Statement(name: ast.AST) -> CStatement:
    ...


@symbol
def Identifier(name: str) -> CIdentifier:
    ...


_i = 0


def _gen_id():
    global _i
    i = f"i_{_i}"
    _i += 1
    return i


def identifier(name: str = None) -> CIdentifier:
    return Identifier(name or _gen_id())


def np_array_from_id(array_id: CIdentifier) -> CInitializableArray:
    return NPArray(Expression(ast.Name(array_id.name, ast.Load())))


def python_content_from_id(array_id: CIdentifier) -> CInitializableContent:
    return PythonContent(Expression(ast.Name(array_id.name, ast.Load())))


def _assign_expresion(expr: CExpression, id_: CIdentifier) -> CStatements:
    return VectorCallable(
        Statement(ast.Assign([ast.Name(id_.name, ast.Store())], expr.name))
    )


register(CallUnary(sw("expr", Expression), sw("id_", Identifier)), _assign_expresion)


register(
    ToPythonContent(sw("i", Int)), lambda i: PythonContent(Expression(ast.Num(i.name)))
)

expressions = typing.Union[matchpy.Expression, typing.Tuple[matchpy.Expression, ...]]


@symbol
def SubstituteIdentifier(
    name: typing.Callable[[str], CStatements]
) -> CSubstituteIdentifier:
    ...


register(
    CallUnary(sw("fn", SubstituteIdentifier), sw("id", Identifier)),
    lambda fn, id: fn.name(id.name),
)


@symbol
def SubstituteStatements(
    name: typing.Callable[..., CStatements]
) -> CSubstituteStatements:
    ...


def all_of_type(type_):
    return lambda args: all(isinstance(a, type_) for a in args)


register(
    CallUnary(sw("fn", SubstituteStatements), VectorCallable(ws("args"))),
    lambda fn, args: fn.name(*(a.name for a in args)),
    matchpy.CustomConstraint(all_of_type(Statement)),
)


def statements_then_init(
    fn: typing.Callable[[], typing.Generator[CStatements, None, CInitializer]]
) -> CInitializer:
    """
    statements_then_init is called to wrap a function
    that yields a bunch of statements and then returns
    an initializer
    """

    def inner(id_: CIdentifier) -> typing.Iterator[CStatements]:
        generator = fn()
        while True:
            try:
                yield next(generator)
            except StopIteration as exc:
                initializer: CInitializer = exc.value
                yield CallUnary(initializer, id_)
                return

    return unary_function(join_statements(inner))


@operation
def ShapeAsTuple(shape: CArray) -> CInitializer:
    ...


def _shape_as_tuple__scalar(_: CContent) -> CInitializer:
    return Expression(ast.Tuple([], ast.Load()))


register(ShapeAsTuple(Scalar(w("_"))), _shape_as_tuple__scalar)


def _shape_as_tuple__sequence(length, getitem):

    inner_seq = CallUnary(getitem, unbound_content())

    @statements_then_init
    def inner():
        inner_shape_id = identifier()
        yield CallUnary(ShapeAsTuple(inner_seq), inner_shape_id)
        length_id = identifier()
        yield CallUnary(Initializer(ToPythonContent(length)), length_id)
        return Expression(
            ast.BinOp(
                ast.Tuple([ast.Name(length_id.name, ast.Load())], ast.Load()),
                ast.Add(),
                ast.Name(inner_shape_id.name, ast.Load()),
            )
        )

    return inner


register(ShapeAsTuple(Sequence(w("length"), w("getitem"))), _shape_as_tuple__sequence)


def _to_np_array_sequence(length, getitem, alloc: ShouldAllocate):
    @NPArray
    @SubstituteIdentifier
    @join_statements
    def inner(array_id: str) -> typing.Iterator[CStatements]:
        if alloc.name:

            # get shape
            shape_tuple_id = identifier()
            yield CallUnary(ShapeAsTuple(Sequence(length, getitem)), shape_tuple_id)
            # allocate array
            array = ast.Call(
                ast.Attribute(ast.Name("np", ast.Load()), "empty", ast.Load()),
                [ast.Name(shape_tuple_id.name, ast.Load())],
                [],
            )
            yield VectorCallable(
                Statement(ast.Assign([ast.Name(array_id, ast.Store())], array))
            )

        length_id = identifier()
        yield CallUnary(Initializer(ToPythonContent(length)), length_id)

        index_id = identifier()
        result_id = identifier()
        # result = getitem(i)
        initialize_result = CallUnary(
            Initializer(
                ToNPArray(
                    CallUnary(getitem, python_content_from_id(index_id)),
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
        def inner(*results_initializer: ast.AST) -> CStatements:
            # for i in range(length):
            return VectorCallable(
                Statement(
                    ast.For(
                        ast.Name(index_id.name, ast.Store()),
                        range_expr,
                        [set_result, *results_initializer, set_array],
                        [],
                    )
                )
            )

        yield CallUnary(inner, initialize_result)

    return inner


# Scalar numpy arrays are converted to scalars, not 0d array
register(
    ToNPArray(Sequence(w("length"), w("getitem")), sw("alloc", ShouldAllocate)),
    _to_np_array_sequence,
)


@operation
def ToSequenceWithDim(arr: CArray, ndim: CContent) -> CArray:
    ...


def _np_array_to_sequence(arr: CExpression, ndim: CInt):
    raise NotImplementedError()

    def inner(e: CArray, i: int) -> CArray:
        if i == ndim.name:
            return Scalar(Content(e))

        length = Expression(
            ast.Subscript(
                ast.Attribute(arr.name, "shape", ast.Load()),
                ast.Index(ast.Num(i)),
                ast.Load(),
            )
        )

        return Sequence(
            PythonContent(length),
            unary_function(lambda idx: inner(CallUnary(GetItem(e), idx), i + 1)),
        )

    return inner(NPArray(arr), 0)


register(
    ToSequenceWithDim(NPArray(sw("arr", Expression)), sw("ndim", Int)),
    _np_array_to_sequence,
)


# @operation
# def FunctionReturnsStatements(
#     body: CStatements, var: CUnbound
# ) -> CFunctionReturnsStatements:
#     ...


# # def function_returns_statements(fn: typing.Callable[[CIdentifier], CStatements]):


def _nparray_getitem(array_init: CInitializer, idx: CContent):
    @statements_then_init
    def inner():
        idx_id = identifier()
        yield CallUnary(Initializer(ToPythonContent(idx)), idx_id)
        array_id = identifier()
        yield CallUnary(array_init, array_id)
        # sub_array = array[idx]
        return SubstituteIdentifier(
            lambda id_: VectorCallable(
                Statement(
                    ast.Assign(
                        [ast.Name(id_, ast.Store())],
                        ast.Subscript(
                            ast.Name(array_id.name, ast.Load()),
                            ast.Index(ast.Name(idx_id.name, ast.Load())),
                            ast.Load(),
                        ),
                    )
                )
            )
        )

    return NPArray(inner)


register(CallUnary(GetItem(NPArray(w("array_init"))), w("idx")), _nparray_getitem)


# for now we just noop
# def _nparray_content(array_init):
#     # scalar =np.asscalar(array)
#     @PythonContent
#     @SubstituteIdentifier
#     @to_tuple
#     def inner(scalar_id: str):
#         array_id = identifier()
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


register(
    Content(NPArray(w("array_init"))), lambda array_init: PythonContent(array_init)
)

CONTENT_OPERATIONS = [
    (Multiply, ast.Mult()),
    (Add, ast.Add()),
    (Remainder, ast.Mod()),
    (Quotient, ast.FloorDiv()),
]

for op, a in CONTENT_OPERATIONS:

    def _op_python_content(l_init, r_init, a_=a):
        @PythonContent
        @statements_then_init
        def inner():
            l_id = identifier()
            r_id = identifier()
            yield CallUnary(l_init, l_id)
            yield CallUnary(r_init, r_id)
            return Expression(
                ast.BinOp(
                    ast.Name(l_id.name, ast.Load()), a_, ast.Name(r_id.name, ast.Load())
                )
            )

        return inner

    register(
        op(PythonContent(w("l_init")), PythonContent(w("r_init"))), _op_python_content
    )

    register(
        ToPythonContent(op(w("x"), w("y"))),
        lambda x, y, op_=op: op_(ToPythonContent(x), ToPythonContent(y)),
    )


@operation
def DefineFunction(ret: CInitializable, *args: CStatement) -> CStatements:
    ...


def _define_function(ret: CInitializable, args: typing.Iterable[CStatement]):

    ret_id = identifier()

    args_ = ast.arguments(
        args=[ast.arg(arg=a.name, annotation=None) for a in args],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
    )

    def inner(*initialize_ret: ast.AST) -> CStatements:
        return VectorCallable(
            Statement(
                ast.Module(
                    body=[
                        ast.FunctionDef(
                            name="fn",
                            args=args_,
                            body=[
                                *initialize_ret,
                                ast.Return(
                                    value=ast.Name(id=ret_id.name, ctx=ast.Load())
                                ),
                            ],
                            decorator_list=[],
                            returns=None,
                        )
                    ]
                )
            )
        )

    initialize_array: CStatements = CallUnary(Initializer(ret), ret_id)
    return CallUnary(SubstituteStatements(inner), initialize_array)


register(DefineFunction(w("ret"), ws("args")), _define_function)


def _vector_indexed_python_content(
    idx_expr: CExpression, args: typing.List[CExpression]
):
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
    VectorIndexed(PythonContent(sw("idx_expr", Expression)), ws("args")),
    _vector_indexed_python_content,
    matchpy.CustomConstraint(all_of_type(Expression)),
)
