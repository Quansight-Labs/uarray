import ast
from .ast import *
from .moa import OuterProduct


def _outer_nparray(_, l_init, r_init):
    @NPArray
    @statements_then_init
    def inner():
        l_id = identifier()
        r_id = identifier()
        yield ApplyUnary(l_init, l_id)
        yield ApplyUnary(r_init, r_id)
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
        return Expression(res)

    return inner


register(
    OuterProduct(w("_"), NPArray(w("l_init")), NPArray(w("r_init"))), _outer_nparray
)
