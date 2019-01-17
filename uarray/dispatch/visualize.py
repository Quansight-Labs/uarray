import functools
import typing
from .core import *

import graphviz


@functools.singledispatch
def description(expr):
    return str(expr)


@description.register
def _box_desc(box: Box):
    return type(box).__qualname__


@description.register
def _operation_desc(op: Operation):
    name = description(key(op))
    n_ports = len(children(op))
    return f"""<
        <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
        <TR>
            <TD COLSPAN="{n_ports}">{name}</TD>
        </TR>
        <TR>
        {' '.join(f'<TD PORT="{i}"></TD>' for i in range(n_ports))}
        </TR>
        </TABLE>
    >"""


@description.register(type(lambda: None))
def _operation_func(op):
    return op.__qualname__


@description.register
def description_type(op: type):
    return op.__qualname__


_id = 0


@functools.singledispatch
def id_(expr) -> str:
    global _id
    _id += 1
    return str(_id)


@id_.register
def id_box(b: Box):
    return str(id(b))


@id_.register
def id_operation(b: Operation):
    return str(id(b))


@functools.singledispatch
def attributes(expr):
    return {"shape": "plaintext", "style": ""}


@attributes.register
def attributes_box(expr: Box):
    return {"shape": "box", "style": "filled"}


@functools.singledispatch
def children_nodes(expr):
    return children(expr)


@children_nodes.register
def _box_children(box: Box):
    return [box.value]


def visualize(expr, dot: graphviz.Digraph, seen: typing.Set[str]) -> str:
    expr_id = id_(expr)
    if expr_id in seen:
        return expr_id
    seen.add(expr_id)
    dot.attr("node", **attributes(expr))
    dot.node(expr_id, description(expr))
    for i, child in enumerate(children_nodes(expr)):
        child_id = visualize(child, dot, seen)
        dot.edge(f"{expr_id}:{i}", child_id)
    return expr_id


try:
    svg_formatter = get_ipython().display_formatter.formatters["image/svg+xml"]
except Exception:
    pass
else:

    def svg(expr):
        d = graphviz.Digraph()
        visualize(expr, d, set())
        return d._repr_svg_()

    svg_formatter.for_type(Box, svg)
