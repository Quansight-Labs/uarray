# pylint: disable=E1120,W0108,W0621,E1121,E1101
"""
Guidelines:

* We want there to be only one way to compile each expression, so don't write two replacement that could apply to the same thing
  I am not sure if there is an order of preference for my specific rules
"""
import itertools
import matchpy
import pprint


##
# Replacer
##

replacer = matchpy.ManyToOneReplacer()
replace = replacer.replace


def _pprint_operation(self, object, stream, indent, allowance, context, level):
    stream.write(f"{type(object).__name__}(")
    self._format_items(object.operands, stream, indent, allowance + 1, context, level)
    stream.write(")")


pprint.PrettyPrinter._pprint_operation = _pprint_operation
pprint.PrettyPrinter._dispatch[
    matchpy.Operation.__repr__
] = pprint.PrettyPrinter._pprint_operation


def replace_debug(expr, use_pprint=False, n=400):
    res = expr
    for _ in range(n):
        new_res = replace(res, 1)
        if new_res == res:
            return res
        res = new_res
        (pprint.pprint if use_pprint else print)(res)
    raise RuntimeError(f"Replaced more than {n} times.")


def register(*args):
    pattern, *constraints, replacement = args
    replacer.add(
        matchpy.ReplacementRule(matchpy.Pattern(pattern, *constraints), replacement)
    )


##
# Utils
##


def idx_from_shape(shape):
    return map(tuple, itertools.product(*map(range, shape)))


def row_major_gamma(idx, shape):
    """
    As defined in 3.30
    """
    if not idx:
        return 0
    return idx[-1] + shape[-1] * row_major_gamma(idx[:-1], shape[:-1])


##
# Symbols
##


class Scalar(matchpy.Symbol):
    """
    Scalar(value) returns a scalar with a value
    """

    def __init__(self, value, name=None):
        self.value = value
        super().__init__(name or repr(value), None)

    def __str__(self):
        return str(self.value)


##
# Operations
##


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


class Index(matchpy.Operation):
    name = "ψ"
    infix = True
    arity = matchpy.Arity(2, True)


class Total(matchpy.Operation):
    name = "τ"
    arity = matchpy.Arity(1, True)


class Vector(matchpy.Operation):
    name = "Vector"
    arity = matchpy.Arity(0, False)

    def __str__(self):
        return f"<{' '.join(map(repr, self.operands))}>"


class ExplodeVector(matchpy.Operation):
    """
    ExplodeVector(length, x) where Shape(x) == <length>
    """

    name = "ExplodeVectorWithLength"
    arity = matchpy.Arity(2, True)


class Reshape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(2, True)
    infix = True


class ReshapeVector(matchpy.Operation):
    """
    Reshape where we know the array is a vector
    """

    name = "ρ_"
    arity = matchpy.Arity(2, True)
    infix = True


class If(matchpy.Operation):
    name = "if"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        expr, if_true, if_false = self.operands
        return f"{expr} ? {if_true} : {if_false}"


class Ravel(matchpy.Operation):
    name = "rav"
    arity = matchpy.Arity(1, True)


class RavelArray(matchpy.Operation):
    """
    Ravel where dim array > 1
    """

    name = "rav_"
    arity = matchpy.Arity(1, True)


class Gamma(matchpy.Operation):
    name = "γ"
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
    name = "BinOp"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"{l} {op.value} {r}"


class BinaryOperationScalarExtension(matchpy.Operation):
    name = "BinOp"
    arity = matchpy.Arity(3, True)


class BinaryOperationArray(matchpy.Operation):
    name = "BinOp"
    arity = matchpy.Arity(3, True)


class Iota(matchpy.Operation):
    name = "ι"
    arity = matchpy.Arity(1, True)


class OuterProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"{l} ·{op} {r}"


##
# Macros
##


def and_(first, second):
    return And(first, lambda: second)


def if_(cond, if_true, if_false):
    return If(cond, lambda: if_true, lambda: if_false)


def vector(*values):
    return Vector(*map(Scalar, values))


def explode_vector(vec):
    return ExplodeVector(vector_first(Shape(vec)), vec)


def to_vector(expr):
    return explode_vector(Ravel(expr))


def is_empty(expr):
    return EquivScalar(Pi(expr), Scalar(0))


def is_scalar(expr):
    return EquivScalar(Dim(expr), Scalar(0))


def is_vector(expr):
    return EquivScalar(Dim(expr), Scalar(1))


def add(l, r):
    return BinaryOperation(l, Scalar(Add), r)


def vector_first(expr):
    return Index(vector(0), expr)


# def vector_first_is_one(expr):
#     return EquivScalar(Scalar(1), Index(vector(0), expr))


# def is_base_vector(expr):
#     """
#     If expr == <1> which is base vector (shape is same as data)
#     """
#     return and_(
#         is_vector(expr),
#         and_(vector_first_is_one(Shape(expr), vector_first_is_one(expr))),
#     )


# def same_shape(expr1, expr2):
#     return Equiv(Shape(expr1), Shape(expr2))


# def is_empty_vector(expr):
#     return Shape(expr, Concrete.vector(0))


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

##
# Replacements
##

# Scalar replacements
register(Shape(scalar), lambda scalar: vector())
register(Not(scalar), lambda scalar: Scalar(not scalar.value))
register(Abs(scalar), lambda scalar: Scalar(abs(scalar.value)))
register(
    And(scalar, scalar1),
    lambda scalar, scalar1: scalar1.value() if scalar.value else Scalar(scalar.value),
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
    EquivScalar(scalar, scalar1), lambda scalar, scalar1: scalar.value == scalar1.value
)

# Vector replacements
register(Shape(Vector(xs)), lambda xs: vector(len(xs)))
register(Index(Vector(scalar), Vector(xs)), lambda x, xs: xs[x.data[0]])
register(
    Gamma(Vector(xs), Vector(xs1)),
    xs_are_scalars,
    xs_are_scalars.with_renamed_vars({"xs": "xs1"}),
    lambda xs, xs1: Scalar(
        row_major_gamma([x_.value for x_ in xs], [x_.value for x_ in xs1])
    ),
)


def _equiv_vector(x, xs, x1, xs1):
    return and_(EquivScalar(x, x1), EquivVector(Vector(*xs), Vector(*xs1)))


register(EquivVector(Vector(), Vector()), lambda: Scalar(True))
register(EquivVector(Vector(x, xs), Vector(x1, xs1)), _equiv_vector)


def pi_vector(xs):
    r = 1
    for x_ in xs:
        r *= x_.value
    return Scalar(r)


register(Pi(Vector(xs)), xs_are_scalars, pi_vector)

# Converstion to concrete
register(
    ExplodeVector(scalar, x),
    lambda scalar, x: vector(*(Index(vector(i), x) for i in range(scalar.value))),
)

# Generic definitions


def _equiv(x, x1):
    return if_(
        and_(is_scalar(x), is_scalar(x1)),
        EquivScalar(x, x1),
        and_(
            EquivVector(to_vector(Shape(x)), to_vector(Shape(x1))),
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
    Index(x, ReshapeVector(x1, x2)), lambda: Index(Mod(Gamma(x, x1), Total(x2)), x2)
)


def _ravel(x):
    return if_(is_scalar(x), Vector(x), if_(is_vector(x), x, RavelArray(x)))


register(Ravel(x), _ravel)


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

register(Shape(BinaryOperationArray(x, scalar, x1), lambda x, scalar, x1: Shape(x)))
register(
    Index(
        x,
        BinaryOperationArray(x1, scalar, x2),
        lambda x, x1, scalar, x2: BinaryOperation(Index(x, x1), scalar, Index(x, x2)),
    )
)
register(
    Shape(BinaryOperationScalarExtension(x, scalar, x1)),
    lambda x, scalar, x1: Shape(x1),
)
register(
    Index(
        x,
        BinaryOperationScalarExtension(x1, scalar, x2),
        lambda x, x1, scalar, x2: BinaryOperation(x1, scalar, Index(x, x2)),
    )
)

register(Shape(ConcatVector(x, x1)), lambda x, x1: add(Shape(x), Shape(x1)))


def _index_concat_vector(x, x1, x2):
    idx = vector_first(x)
    size_first = vector_first(Shape(x1))
    modified_index = Subtract(idx, size_first)
    return if_(LessThen(idx, size_first), Index(x, x1), Index(modified_index, x2))


register(Index(x, ConcatVector(x1, x2)), lambda x, x1: add(Shape(x), Shape(x1)))

register(Shape(Iota(x)), lambda x: Vector(x))
register(Index(x, Iota(x1)), lambda x, x1: vector_first(x))

register(Shape(Take(x, x1)), lambda x, x1: Vector(Abs(vector_first(x))))
register(
    Index(x, Take(x1, x2)),
    lambda x, x1, x2: if_(
        LessThen(vector_first(x1), Scalar(0)),
        Index(Vector(Add(Add(Total(x2), x1), vector_first(x))), x2),
        Index(x, x2),
    ),
)
register(
    Shape(Drop(x, x1)), lambda x, x1: Vector(Subtract(Total(x1), Abs(vector_first(x))))
)
register(
    Index(x, Drop(x1, x2)),
    lambda x, x1, x2: if_(
        LessThen(vector_first(x1), Scalar(0)),
        Index(x, x2),
        Index(Vector(Add(x1, vector_first(x))), x2),
    ),
)


register(Shape(Index(x, x1)), lambda x, x1: Drop(Total(x), Shape(x1)))
register(Index(x, Index(x1, x2)), lambda x, x1, x2: Index(ConcatVector(x1, x), x2))


def outer_product_index(x, x1, scalar, x3):
    """
    MoA Outer product but also support partial indexing.

    This is because it's hard right now to match based on the length
    of an array, so hard to filter for valid indices when matching.
    It also makes some sense to support it partially, so that it can reduce a partial expression.

    Basically we try to take the all that the left array needs from the index, and then pass the rest
    onto the right array. If they both end up being scalars, we have fully indexed the outer product and we
    can compute the result. Otherwise, we recurse with a new outer product that has the arrays partially indexed.
    """
    index, left, right = x, x1, x3
    d = Dim(left)
    i = Take(d, index)
    j = Drop(d, index)
    new_left = Index(i, left)
    new_right = Index(j, right)
    return if_(
        and_(is_scalar(new_left), is_scalar(new_right)),
        scalar.value(new_left, new_right),
        OuterProduct(new_left, scalar, new_right),
    )


register(Index(x, OuterProduct(x1, scalar, x3)), outer_product_index)


##
# Gaurds and conversions
##

# class NotDefined(matchpy.Symbol):
#     def __init__(self, message):
#         self.message = message
#         super().__init__(message, None)


# class WithConcrete(matchpy.Operation):
#     """
#     WithConcrete(replacement_fn, *exprs)
#     Transforms some expressions into concrete representations and calls replacement_fn
#     with those concrete values when they are all converted.

#         >>> WithConcrete(
#                 Thunk(lambda some_expr_concrete: Concrete.scalar(sum(some_expr_concrete.data))),
#                 AsConcrete(SomeExpr)
#             )
#     """

#     name = "WithConcrete"
#     arity = matchpy.Arity(1, False)


# def assert_defined(message, conditional, expr):
#     return If(conditional, lambda: expr, lambda: NotDefined(message))


# def with_concrete(replacement_fn, *exprs):
#     return WithConcrete(Thunk(replacement_fn), *map(AsConcrete, exprs))

# register(
#     If(x, thunk, thunk1),
#     lambda x, thunk, thunk1: assert_defined("If takes scalar value", is_scalar(x), with_concrete(lambda x_concrete: thunk.fn() if x_concrete.data[0] else thunk1.fn(), x))
# )
