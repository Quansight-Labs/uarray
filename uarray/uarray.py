# pylint: disable=E1120,W0108,W0621,E1121,E1101
"""
Guidelines:

* We want there to be only one way to compile each expression, so don't write two replacement that could apply to the same thing
  I am not sure if there is an order of preference for my specific rules
"""
import itertools
import pprint

import matchpy

##
# Replacer
##

replacer = matchpy.ManyToOneReplacer()
replace = replacer.replace


def _pprint_operation(self, object, stream, indent, allowance, context, level):
    """
    Modified from pprint dict https://github.com/python/cpython/blob/3.7/Lib/pprint.py#L194
    """
    operands = object.operands
    if not operands:
        stream.write(repr(object))
        return
    cls = object.__class__
    stream.write(cls.__name__ + "(")
    self._format_items(
        operands, stream, indent + len(cls.__name__), allowance + 1, context, level
    )
    stream.write(")")


pprint.PrettyPrinter._pprint_operation = _pprint_operation
pprint.PrettyPrinter._dispatch[
    matchpy.Operation.__repr__
] = pprint.PrettyPrinter._pprint_operation


def replace_debug(expr, use_pprint=False, n=100):
    res = expr
    for _ in range(n):
        printer = pprint.pprint if use_pprint else print
        printer(res)
        new_res = replace(res, 1, print_steps=True)
        if new_res == res:
            break
        res = new_res
    return res


def register(*args):
    pattern, *constraints, replacement = args
    replacer.add(
        matchpy.ReplacementRule(matchpy.Pattern(pattern, *constraints), replacement)
    )


# doesn't work cause expressions are re-created when replaced so adding on to passed in expression doesn't work
# def print_tree(expr):
#     """
#     Print's the expressiond preceeded by the express
#     it replaced, and recursing.
#     """
#     if hasattr(expr, "_previous"):
#         print_tree(expr._previous)
#     print(expr)


##
# Utils
##


def product(xs):
    r = 1
    for x_ in xs:
        r *= x_
    return r


def idx_from_shape(shape):
    return map(tuple, itertools.product(*map(range, shape)))


def row_major_gamma(idx, shape):
    """
    As defined in 3.30
    """
    assert len(idx) == len(shape)
    if not idx:
        return 0
    assert idx < shape
    return idx[-1] + (shape[-1] * row_major_gamma(idx[:-1], shape[:-1]))


def row_major_gamma_inverse(n, shape):
    """
    As defined in 3.41
    """
    assert n >= 0
    assert n < product(shape)
    for x_ in shape:
        assert x_ > 0

    if len(shape) == 1:
        return (n,)

    *next_shape, dim = shape
    return (*row_major_gamma_inverse(n // dim, next_shape), n % dim)


##
# Symbols
##


class Scalar(matchpy.Symbol):
    """
    Scalar(value, name=None) returns a scalar with a value
    """

    def __init__(self, value, display_value=None):
        self.value = value
        self._display_value = display_value or value
        super().__init__(repr(self._display_value), None)

    def __str__(self):
        return str(self._display_value)


##
# Operations
##


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


class Index(matchpy.Operation):
    """
    Top level indexing is transformed into either partial indexing or
    full indexing. You should only define rules on either of those, not the
    top level, or else there could be multiple ways of replacing `Index`.

    TODO: replace with macro maybe so we can't override?
    """

    name = "ψ"
    infix = True
    arity = matchpy.Arity(2, True)


class PartialIndex(matchpy.Operation):
    name = "ψp"
    infix = True
    arity = matchpy.Arity(2, True)


class FullIndex(matchpy.Operation):
    name = "ψf"
    infix = True
    arity = matchpy.Arity(2, True)


class Total(matchpy.Operation):
    name = "τ"
    arity = matchpy.Arity(1, True)


class Vector(matchpy.Operation):
    name = "Vector"
    arity = matchpy.Arity(0, False)

    def __str__(self):
        return f"<{' '.join(map(str, self.operands))}>"


class ExplodeVector(matchpy.Operation):
    """
    ExplodeVector(length, x) where Shape(x) == <length>
    """

    name = "ExplodeVector"
    arity = matchpy.Arity(2, True)


class AbstractWithDimension(matchpy.Operation):
    """
    AbstractWithDimension(dimension, variable_name=name) represents an array
    with known dimensionality but unknown contents or shape.
    """

    name = "AbstractWithDimension"
    arity = matchpy.Arity(1, True)

    def __str__(self):
        name = self.variable_name or "ε"
        return f"{name}^{self.operands[0]}"


class Reshape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(2, True)
    infix = True


class ReshapeVector(matchpy.Operation):
    """
    Reshape where we know the array is a vector
    """

    name = "ρ"
    arity = matchpy.Arity(2, True)
    infix = True


class If(matchpy.Operation):
    name = "if"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        expr, if_true, if_false = self.operands
        return f"({expr} ? {if_true} : {if_false})"


class Ravel(matchpy.Operation):
    name = "rav"
    arity = matchpy.Arity(1, True)


class RavelArray(matchpy.Operation):
    """
    Ravel where dim array > 1
    """

    name = "rav-a"
    arity = matchpy.Arity(1, True)


class Gamma(matchpy.Operation):
    name = "γ"
    arity = matchpy.Arity(2, True)


class GammaInverse(matchpy.Operation):
    name = "γ'"
    arity = matchpy.Arity(2, True)


class And(matchpy.Operation):
    """
    And(first, lambda: second)
    """

    name = "and"
    infix = True
    arity = matchpy.Arity(2, True)


class Not(matchpy.Operation):
    name = "not"
    arity = matchpy.Arity(1, True)


class Mod(matchpy.Operation):
    name = "mod"
    arity = matchpy.Arity(2, True)


class Add(matchpy.Operation):
    name = "+"
    infix = True
    arity = matchpy.Arity(2, True)


class Multiply(matchpy.Operation):
    name = "×"
    infix = True
    arity = matchpy.Arity(2, True)


class Abs(matchpy.Operation):
    name = "abs"
    arity = matchpy.Arity(1, True)


class Subtract(matchpy.Operation):
    name = "-"
    infix = True
    arity = matchpy.Arity(2, True)


class LessThen(matchpy.Operation):
    name = "<"
    infix = True
    arity = matchpy.Arity(2, True)


class Dim(matchpy.Operation):
    """
    Dimensionality
    """

    name = "δ"
    arity = matchpy.Arity(1, True)


class Take(matchpy.Operation):
    name = "↑"
    infix = True
    arity = matchpy.Arity(2, True)


class Drop(matchpy.Operation):
    """
    Drop(vector, array)
    """

    name = "↓"
    infix = True
    arity = matchpy.Arity(2, True)


class Equiv(matchpy.Operation):
    name = "≡"
    infix = True
    arity = matchpy.Arity(2, True)


class EquivScalar(matchpy.Operation):
    name = "≡s"
    infix = True
    arity = matchpy.Arity(2, True)


class EquivVector(matchpy.Operation):
    name = "≡v"
    infix = True
    arity = matchpy.Arity(2, True)


class Pi(matchpy.Operation):
    name = "π"
    arity = matchpy.Arity(1, True)


# class Concat(matchpy.Operation):
#     name = "‡"
#     infix = True
#     arity = matchpy.Arity(2, True)


class ConcatVector(matchpy.Operation):
    name = "‡v"
    infix = True
    arity = matchpy.Arity(2, True)


# class ConcatArray(matchpy.Operation):
#     name = "‡a"
#     infix = True
#     arity = matchpy.Arity(2, True)


class BinaryOperation(matchpy.Operation):
    name = "BinaryOperation"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"({l} {op.value} {r})"


class BinaryOperationScalarExtension(matchpy.Operation):
    name = "BinaryOperationScalarExtension"
    arity = matchpy.Arity(3, True)


class BinaryOperationArray(matchpy.Operation):
    name = "BinaryOperationArray"
    arity = matchpy.Arity(3, True)


class Iota(matchpy.Operation):
    """
    Iota(n) returns a vector of 0 to n-1.
    """

    name = "ι"
    arity = matchpy.Arity(1, True)


class OuterProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"({l} ·{op} {r})"


class InnerProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(4, True)

    def __str__(self):
        l, op_l, op_r, r = self.operands
        return f"({l} {op_l}·{op_r} {r})"


##
# Macros
##


def thunk(value):
    return Scalar(lambda: value, value)


def and_(first, second):
    return And(first, thunk(second))


def if_(cond, if_true, if_false):
    return If(cond, thunk(if_true), thunk(if_false))


def vector(*values):
    return Vector(*map(Scalar, values))


def explode_vector(vec):
    return ExplodeVector(vector_first(Shape(vec)), vec)


def to_vector(expr):
    return ExplodeVector(Total(expr), Ravel(expr))


def as_vector(expr):
    return Reshape(Shape(expr), to_vector(expr))


def sum_vector(expr):
    return Pi(explode_vector(expr))


def is_scalar(expr):
    return EquivScalar(Dim(expr), Scalar(0), variable_name="is_scalar")


def is_vector(expr):
    return EquivScalar(Dim(expr), Scalar(1), variable_name="is_vector")


def add(l, r):
    return BinaryOperation(l, Scalar(Add), r)


def vector_first(expr):
    return FullIndex(vector(0), expr)


##
# Wildcards
##


x = matchpy.Wildcard.dot("x")
x1 = matchpy.Wildcard.dot("x1")
x2 = matchpy.Wildcard.dot("x2")
x3 = matchpy.Wildcard.dot("x3")
x4 = matchpy.Wildcard.dot("x4")

xs = matchpy.Wildcard.star("xs")
xs1 = matchpy.Wildcard.star("xs1")

scalar = matchpy.Wildcard.symbol("scalar", Scalar)
scalar1 = matchpy.Wildcard.symbol("scalar1", Scalar)
scalar2 = matchpy.Wildcard.symbol("scalar2", Scalar)


##
# Constraints
##
xs_are_scalars = matchpy.CustomConstraint(
    lambda xs: all(isinstance(x_, Scalar) for x_ in xs)
)
xs1_are_scalars = matchpy.CustomConstraint(
    lambda xs1: all(isinstance(x_, Scalar) for x_ in xs1)
)

##
# Replacements
##

# Abstract
register(Shape(Shape(AbstractWithDimension(x))), lambda x: Vector(x))

# Scalar replacements
register(Shape(scalar), lambda scalar: vector())
register(Not(scalar), lambda scalar: Scalar(not scalar.value))
register(Abs(scalar), lambda scalar: Scalar(abs(scalar.value)))
register(
    And(scalar, scalar1),
    lambda scalar, scalar1: scalar1.value() if scalar.value else scalar,
)
register(
    LessThen(scalar, scalar1),
    lambda scalar, scalar1: Scalar(scalar.value < scalar1.value),
)
register(
    Mod(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value % scalar1.value)
)

register(
    Add(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value + scalar1.value)
)
register(
    Subtract(scalar, scalar1),
    lambda scalar, scalar1: Scalar(scalar.value - scalar1.value),
)
register(
    If(scalar, scalar1, scalar2),
    lambda scalar, scalar1, scalar2: scalar1.value()
    if scalar.value
    else scalar2.value(),
)
register(
    EquivScalar(scalar, scalar1),
    lambda scalar, scalar1: Scalar(scalar.value == scalar1.value),
)

# Vector replacements
register(Shape(Vector(xs)), lambda xs: vector(len(xs)))
register(FullIndex(Vector(scalar), Vector(xs)), lambda scalar, xs: xs[scalar.value])
register(
    Gamma(Vector(xs), Vector(xs1)),
    xs_are_scalars,
    xs1_are_scalars,
    lambda xs, xs1: Scalar(
        row_major_gamma([x_.value for x_ in xs], [x_.value for x_ in xs1])
    ),
)
register(
    GammaInverse(scalar, Vector(xs)),
    xs_are_scalars,
    lambda scalar, xs: vector(
        *row_major_gamma_inverse(scalar.value, [x_.value for x_ in xs])
    ),
)


def _equiv_vector(x, xs, x1, xs1):
    return and_(EquivScalar(x, x1), EquivVector(Vector(*xs), Vector(*xs1)))


register(EquivVector(Vector(), Vector()), lambda: Scalar(True))
register(EquivVector(Vector(x, xs), Vector(x1, xs1)), _equiv_vector)
register(
    Pi(Vector(xs)), xs_are_scalars, lambda xs: Scalar(product(x_.value for x_ in xs))
)

# superflous vector replacements
# only valid when value positive
# TODO: Replace all with ExplodeVector somewhere in chain
# register(
#     Take(Vector(scalar), Vector(xs)), lambda scalar, xs: Vector(*xs[: scalar.value])
# )
# register(
#     Drop(Vector(scalar), Vector(xs)), lambda scalar, xs: Vector(*xs[: -scalar.value])
# )

# register(ConcatVector(Vector(xs), Vector(xs1)), lambda xs, xs1: Vector(*xs, *xs1))


# Converstion to concrete
register(
    ExplodeVector(scalar, x),
    lambda scalar, x: Vector(*(FullIndex(vector(i), x) for i in range(scalar.value))),
)

# Generic definitions

register(Total(x), lambda x: sum_vector(Shape(x)))


def _equiv(x, x1):
    # operations and operands are the same, and variable names are the same (if not none)
    if x == x1:
        return Scalar(True)
    return if_(
        and_(is_scalar(x), is_scalar(x1)),
        EquivScalar(x, x1),
        and_(
            EquivVector(explode_vector(Shape(x)), explode_vector(Shape(x1))),
            EquivVector(to_vector(x), to_vector(x1)),
        ),
    )


register(Equiv(x, x1), _equiv)
register(Dim(x), lambda x: vector_first(Shape(Shape(x))))


def reshape(x, x1):
    """
    TODO: Handle if x has zero, then return empty array
    """
    return if_(is_vector(x), ReshapeVector(x, x1), ReshapeVector(x, Ravel(x1)))


register(Reshape(x, x1), reshape)


register(Shape(ReshapeVector(x, x1)), lambda x, x1: x)

register(
    FullIndex(x, ReshapeVector(x1, x2)),
    lambda x, x1, x2: FullIndex(Vector(Mod(Gamma(x, x1), Total(x2))), x2),
)


def _ravel(x):
    return if_(is_scalar(x), Vector(x), if_(is_vector(x), x, RavelArray(x)))


register(Ravel(x), _ravel)


register(
    FullIndex(x, RavelArray(x1)),
    lambda x, x1: FullIndex(GammaInverse(vector_first(x), Shape(x1)), x1),
)


def _binary_operation(x, scalar, x1):
    return if_(
        is_scalar(x),
        if_(
            is_scalar(x1),
            scalar.value(x, x1),
            BinaryOperationScalarExtension(x, scalar, x1),
        ),
        if_(
            is_scalar(x1),
            BinaryOperationScalarExtension(x1, scalar, x),
            BinaryOperationArray(x, scalar, x1),
        ),
    )


register(BinaryOperation(x, scalar, x1), _binary_operation)

register(Shape(BinaryOperationArray(x, scalar, x1)), lambda x, scalar, x1: Shape(x))
register(
    FullIndex(x, BinaryOperationArray(x1, scalar, x2)),
    lambda x, x1, scalar, x2: BinaryOperation(
        FullIndex(x, x1), scalar, FullIndex(x, x2)
    ),
)
register(
    Shape(BinaryOperationScalarExtension(x, scalar, x1)),
    lambda x, scalar, x1: Shape(x1),
)
register(
    FullIndex(x, BinaryOperationScalarExtension(x1, scalar, x2)),
    lambda x, x1, scalar, x2: BinaryOperation(x1, scalar, FullIndex(x, x2)),
)

register(Shape(ConcatVector(x, x1)), lambda x, x1: add(Shape(x), Shape(x1)))


def _index_concat_vector(x, x1, x2):
    idx = vector_first(x)
    size_first = vector_first(Shape(x1))
    modified_index = Subtract(idx, size_first)
    return if_(
        LessThen(idx, size_first), FullIndex(x, x1), FullIndex(modified_index, x2)
    )


register(Shape(ConcatVector(x, x1)), lambda x, x1: add(Shape(x), Shape(x1)))
register(FullIndex(x, ConcatVector(x1, x2)), _index_concat_vector)

register(Shape(Iota(x)), lambda x: Vector(x))
register(FullIndex(x, Iota(x1)), lambda x, x1: vector_first(x))

# Only vectors
register(Shape(Take(x, x1)), lambda x, x1: Vector(Abs(vector_first(x))))
register(
    FullIndex(x, Take(x1, x2)),
    lambda x, x1, x2: if_(
        LessThen(vector_first(x1), Scalar(0)),
        FullIndex(Vector(Add(Add(Total(x2), x1), vector_first(x))), x2),
        FullIndex(x, x2),
    ),
)
register(
    Shape(Drop(x, x1)), lambda x, x1: Vector(Subtract(Total(x1), Abs(vector_first(x))))
)
register(
    FullIndex(x, Drop(x1, x2)),
    lambda x, x1, x2: if_(
        LessThen(vector_first(x1), Scalar(0)),
        FullIndex(x, x2),
        FullIndex(Vector(Add(x1, vector_first(x))), x2),
    ),
)


# full indexing is if shape of index is == shape of shape of value
register(
    Index(x, x1),
    lambda x, x1: if_(
        Equiv(Shape(x), Shape(Shape(x1))), FullIndex(x, x1), PartialIndex(x, x1)
    ),
)

# TODO: make these not depend on vector but just shape of index array
# Change Index to be IndexWithShapes.
register(PartialIndex(Vector(), x), lambda x: x)
register(FullIndex(Vector(), x), lambda x: x)

register(Shape(FullIndex(x, x1)), lambda x, x1: vector())
register(Shape(PartialIndex(x, x1)), lambda x, x1: Drop(Vector(Total(x)), Shape(x1)))
register(
    PartialIndex(x, PartialIndex(x1, x2)),
    lambda x, x1, x2: Index(ConcatVector(x1, x), x2),
)

register(
    Shape(OuterProduct(x, scalar, x2)),
    lambda x, scalar, x2: ConcatVector(Shape(x), Shape(x2)),
)


def outer_product_index(is_partial, index, left, scalar, right):
    """
    MoA Outer product but also support partial indexing.

    Basically we try to take the all that the left array needs from the index, and then pass the rest
    onto the right array. If they both end up being scalars, we have fully indexed the outer product and we
    can compute the result. Otherwise, we recurse with a new outer product that has the arrays partially indexed.
    """
    d = Shape(Shape(left))
    i = Take(d, index)
    j = Drop(d, index)
    new_left = (PartialIndex if is_partial else FullIndex)(i, left)
    new_right = (PartialIndex if is_partial else FullIndex)(j, right)
    if is_partial:
        return OuterProduct(new_left, scalar, new_right)
    return scalar.value(new_left, new_right)


register(
    FullIndex(x, OuterProduct(x1, scalar, x3)),
    lambda x, x1, scalar, x3: outer_product_index(False, x, x1, scalar, x3),
)
register(
    PartialIndex(x, OuterProduct(x1, scalar, x3)),
    lambda x, x1, scalar, x3: outer_product_index(True, x, x1, scalar, x3),
)

