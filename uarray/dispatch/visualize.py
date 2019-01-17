import functools
from .core import *

import graphviz


@functools.singledispatch
def description(expr):
    return str(expr)


@description.register
def _box_desc(box: Box):
    return "Box"


@description.register
def _operation_desc(op: Operation):
    return description(key(op))


@description.register(type(lambda: None))
def _operation_func(op):
    return op.__qualname__


@functools.singledispatch
def id_(expr) -> str:
    return str(id(expr))


@functools.singledispatch
def attributes(expr):
    return {"shape": "plaintext"}


@attributes.register
def attributes_box(expr: Box):
    return {"shape": "box"}


@functools.singledispatch
def children_nodes(expr):
    return children(expr)


@children_nodes.register
def _box_children(box: Box):
    return [box.value]


def visualize(expr, dot: graphviz.Digraph) -> str:
    expr_id = id_(expr)
    dot.attr("node", **attributes(expr))
    dot.node(expr_id, description(expr))
    for child in children_nodes(expr):
        child_id = visualize(child, dot)
        dot.edge(expr_id, child_id)
    return expr_id


try:
    svg_formatter = get_ipython().display_formatter.formatters["image/svg+xml"]
except Exception:
    pass
else:

    def svg(expr):
        d = graphviz.Digraph()
        visualize(expr, d)
        return d._repr_svg_()

    svg_formatter.for_type(Box, svg)
