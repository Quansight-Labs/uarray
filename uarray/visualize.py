import itertools

import matchpy

try:
    import graphviz
except ImportError as e:
    graphviz = None


def visualize_expression(expr, comment='uarray expression', with_attrs=True, with_uarray=True):
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
        raise ImportError('The graphviz package is required to draw expressions')

    from . import moa, core

    dot = graphviz.Digraph(comment=comment)
    counter = itertools.count()
    default_node_attr = dict(color='black', fillcolor='white', fontcolor='black')

    def _label_node(dot, expr):
        unique_id = str(next(counter))

        if hasattr(expr, '_repr_gviz_node_'):
            node_description, node_attr = expr._repr_gviz_node_()
        elif isinstance(expr, core.Sequence) and with_uarray:
            if isinstance(expr[1], core.UnaryFunction):
                node_description = f'NDArray\n{expr[1][0][1][0][0][0][0][0][0][0].variable_name}^< {" ".join([str(_[0].name) for _ in expr[1][0][0]])} >'
                node_attr = dict(shape='box')
            else:
                node_description = f'Vector\n< {" ".join([str(_[0].name) for _ in expr[1]])} >'
                node_attr = dict(shape='box')
        elif isinstance(expr, core.Unbound) and with_uarray:
            node_description = f'NDArray\n{expr.variable_name}'
            node_attr = dict(shape='box')
        elif isinstance(expr, matchpy.Symbol):
            node_description = f'Symbol: {expr.__class__.__name__}\n{expr.name}'
            if expr.variable_name:
                node_description += f', variable_name={expr.variable_name}'
            node_attr = dict(shape='box')
        elif isinstance(expr, matchpy.Operation):
            node_description = f'Operation: {expr.__class__.__name__}\n'
            if expr.variable_name:
                node_description += ', variable_name={expr.variable_name}'
            node_attr = dict(shape='oval')
        else:
            raise ValueError(f'uarray matchpy expression does not have _repr_gviz_node_: "{repr(self)}"')

        if with_attrs:
            dot.attr('node', **{**default_node_attr, **node_attr})
        dot.node(unique_id, node_description)
        return unique_id

    def _visualize_node(dot, expr):
        expr_id = _label_node(dot, expr)

        if isinstance(expr, matchpy.Operation) and (not isinstance(expr, (core.Unbound, core.Sequence)) or not with_uarray):
            for sub_expr in expr:
                sub_expr_id = _visualize_node(dot, sub_expr)
                dot.edge(expr_id, sub_expr_id)
        return expr_id

    _visualize_node(dot, expr)
    return dot
