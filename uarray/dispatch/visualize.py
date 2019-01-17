import itertools
import functools
from .core import *

try:
    import graphviz
except ImportError as e:
    graphviz = None


# graphviz.Digraph()

# if graphviz is None:
#     raise ImportError("The graphviz package is required to draw expressions")


@functools.singledispatch
def description(expr):
    return str(expr)


@description.register
def _box_desc(box: Box):
    return "Box"


@description.register
def _operation_desc(op: Operation):
    return str(key(op))


@description.register
def _wrapper_desc(w: Wrapper):
    return type(w).__name__


@functools.singledispatch
def id_(expr) -> str:
    return str(id(expr))


@functools.singledispatch
def attributes(expr):
    return dict(color="black", fillcolor="white", fontcolor="black")


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

    # default_node_attr = dict(color="black", fillcolor="white", fontcolor="black")

    # def _label_node(dot, expr):
    #     unique_id = str(next(counter))
    #     shape = "oval"
    #     node_description = type(expr).__name__
    #     if isinstance(expr, matchpy.Symbol):
    #         node_description = str(expr.value())
    #     if expr.variable_name:
    #         shape = "box"
    #         node_description = expr.variable_name

    #     if with_attrs:
    #         dot.attr("node", shape=shape, **default_node_attr)
    #     dot.node(unique_id, node_description)
    #     return unique_id

    # def _visualize_node(dot, expr):
    #     expr_id = _label_node(dot, expr)
    #     if not isinstance(expr, matchpy.Symbol):
    #         for sub_expr in expr:
    #             sub_expr_id = _visualize_node(dot, sub_expr)
    #             dot.edge(expr_id, sub_expr_id)
    #     return expr_id

    # _visualize_node(dot, expr)
    # return dot
