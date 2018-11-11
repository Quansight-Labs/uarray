import ast
from .ast import *
from .moa import OuterProduct


def _outer_nparray(_, l_init, r_init):
    @NPArray
    @SubstituteIdentifier
    @to_tuple
    def inner(res_id: str):
        l_id = Identifier()
        r_id = Identifier()
        yield CallUnary(l_init, l_id)
        yield CallUnary(r_init, r_id)
        res = ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id="np", ctx=ast.Load()),
                    attr="multiply",
                    ctx=ast.Load(),
                ),
                attr="outer",
                ctx=ast.Load(),
            ),
            args=[
                ast.Name(id=l_id.name, ctx=ast.Load()),
                ast.Name(id=r_id.name, ctx=ast.Load()),
            ],
            keywords=[],
        )
        yield Statement(ast.Assign([ast.Name(res_id, ast.Store())], res))

    return inner


register(
    OuterProduct(w("_"), NPArray(w("l_init")), NPArray(w("r_init"))), _outer_nparray
)
