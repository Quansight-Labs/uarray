import itertools

import matchpy
from .printing import to_repr

try:
    import graphviz
except ImportError as e:
    graphviz = None


def visualize_expression(
    expr, comment="uarray expression", with_attrs=True, with_uarray=True
):
    """Returns a graphviz representation of the uarray expression

    Expects that each node(Symbol/Operation) has an attribute
    `_repr_gviz_node_()`. This method returns a tuple with string
    decription https://www.graphviz.org/doc/info/shapes.html that
    allows html and a dictionary that describes node attributes
    https://www.graphviz.org/doc/info/attrs.html.

    Attributes
    ==========
    expr:
       uarray expression
    comment:
       name to give graphviz dot
    with_attrs:
       whether to apply graphviz attributes to nodes (enable/disable) stlying
    with_uarray:
       whether to display graphviz with specialized uarray logic

    Example
    =======
    (
       'hello world',
       {'color': 'red', 'fontsize': 100}
    )

    """
    if graphviz is None:
        raise ImportError("The graphviz package is required to draw expressions")

    from . import moa, core

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color="black", fillcolor="white", fontcolor="black")

    def _label_node(dot, expr):
        unique_id = str(next(counter))
        shape = "oval"
        node_description = type(expr).__name__
        if isinstance(expr, matchpy.Symbol) or isinstance(expr, core.Unbound):
            node_description = str(expr)
        if isinstance(expr, core.Unbound):
            shape = "box"

        if with_attrs:
            dot.attr("node", shape=shape, **default_node_attr)
        dot.node(unique_id, node_description)
        return unique_id

    def _visualize_node(dot, expr):
        expr_id = _label_node(dot, expr)
        if not isinstance(expr, matchpy.Symbol):
            for sub_expr in expr:
                sub_expr_id = _visualize_node(dot, sub_expr)
                dot.edge(expr_id, sub_expr_id)
        return expr_id

    _visualize_node(dot, expr)
    return dot
