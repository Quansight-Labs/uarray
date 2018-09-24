# pylint: disable=E1120,W0108,W0621,E1121
"""
Guidelines:

* We want there to be only one way to compile each expression, so don't write two replacement that could apply to the same thing
  I am not sure if there is an order of preference for my specific rules
"""
import itertools

import matchpy

##
# Replacer
##

replacer = matchpy.ManyToOneReplacer()
replace = replacer.replace


def replace_debug(expr, n=10, use_repr=False):
    for i in range(n):
        print((repr if use_repr else str)(replace(expr, i)))


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


class Concrete(matchpy.Symbol):
    def __init__(self, shape, data):
        self.shape = shape
        self.data = data

        super().__init__(f"[{' '.join(map(repr, data))}; ρ={repr(shape)}]", None)

    @classmethod
    def vector(cls, *values):
        return cls((len(values)), tuple(values))

    @classmethod
    def scalar(cls, value):
        return cls(tuple(), (value,))

    @property
    def dim(self):
        return len(self.shape)

    @property
    def is_vector(self):
        return self.dim == 1

    @property
    def is_scalar(self):
        return self.dim == 0


class Thunk(matchpy.Symbol):
    def __init__(self, fn):
        self.fn = fn
        super().__init__(matchpy.utils.get_short_lambda_source(fn) or repr(fn), None)


class BinaryOperation(matchpy.Symbol):
    def __init__(self, operation):
        self.operation = operation
        super().__init__(str(operation), None)


##
# Operations
##


class If(matchpy.Operation):
    name = "if"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        expr, if_true, if_false = self.operands
        return f"{expr} ? {if_true} : {if_false}"


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


class Index(matchpy.Operation):
    name = "ψ"
    infix = True
    arity = matchpy.Arity(2, True)


class Ravel(matchpy.Operation):
    name = "rav"
    arity = matchpy.Arity(1, True)


class Gamma(matchpy.Operation):
    name = "γ"
    arity = matchpy.Arity(2, True)


class AsConcrete(matchpy.Operation):
    name = "AsConcrete"
    arity = matchpy.Arity(1, True)


class AsConcreteWithShape(matchpy.Operation):
    name = "AsConcreteWithShape"
    arity = matchpy.Arity(2, True)


class AsConcreteWithValues(matchpy.Operation):
    name = "AsConcreteWithValues"
    arity = matchpy.Arity(1, False)


class And(matchpy.Operation):
    name = "and"
    infix = True
    arity = matchpy.Arity(2, True)


class Add(matchpy.Operation):
    name = "+"
    infix = True
    arity = matchpy.Arity(2, True)


class Dim(matchpy.Operation):
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


class Concat(matchpy.Operation):
    name = "‡"
    infix = True
    arity = matchpy.Arity(2, True)


class OuterProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"{l} ·{op} {r}"


##
# Macros
##


def is_vector(expr):
    return Equiv(Dim(expr), Concrete.scalar(2))


def same_shape(expr1, expr2):
    return Equiv(Shape(expr1), Shape(expr2))


def is_empty_vector(expr):
    return Shape(expr, Concrete.vector(0))


##
# Wildcards
##


x = matchpy.Wildcard.dot("x")
x1 = matchpy.Wildcard.dot("x1")
x2 = matchpy.Wildcard.dot("x2")
x3 = matchpy.Wildcard.dot("x3")
x4 = matchpy.Wildcard.dot("x4")
xs = matchpy.Wildcard.star("xs")
xs2 = matchpy.Wildcard.star("xs2")

thunk = matchpy.Wildcard.symbol("thunk", Thunk)
thunk1 = matchpy.Wildcard.symbol("thunk1", Thunk)


concrete = matchpy.Wildcard.symbol("concrete", Concrete)
concrete1 = matchpy.Wildcard.symbol("concrete1", Concrete)
concrete2 = matchpy.Wildcard.symbol("concrete2", Concrete)


binary_operation = matchpy.Wildcard.symbol("binary_operation", BinaryOperation)


##
# Constraints
##


concrete_is_scalar = matchpy.CustomConstraint(lambda concrete: concrete.is_scalar)
concrete_is_true_scalar = matchpy.CustomConstraint(
    lambda concrete: concrete.is_scalar and concrete.data[0]
)

concrete_is_empty_vector = matchpy.CustomConstraint(
    lambda concrete: concrete.shape == (0,)
)
concrete_is_single_vector = matchpy.CustomConstraint(
    lambda concrete: concrete.shape == (1,)
)
concrete_is_vector = matchpy.CustomConstraint(lambda concrete: concrete.is_vector)
concrete_index_is_full = matchpy.CustomConstraint(
    lambda concrete, concrete1: concrete.is_vector
    and concrete.shape[0] == len(concrete1.shape)
    and concrete1.dim * (0,) <= concrete1.shape
    and concrete.data < concrete1.shape
)
concrete_same_length_vectors = matchpy.CustomConstraint(
    lambda concrete, concrete1: concrete.is_vector
    and concrete1.is_vector
    and concrete.shape == concrete1.shape
)

##
# Replacements
##

# Concrete indexing and shape

register(Shape(concrete), lambda concrete: Concrete.vector(*concrete.shape))

register(
    Index(concrete, concrete1),
    concrete_index_is_full,
    matchpy.CustomConstraint(lambda concrete1: concrete1.dim > 1),
    lambda concrete, concrete1: Concrete(
        Gamma(concrete, Shape(concrete1)), Ravel(concrete1)
    ),
)
register(
    Index(concrete, concrete1),
    concrete_index_is_full,
    matchpy.CustomConstraint(lambda concrete1: concrete1.is_vector),
    lambda concrete, concrete1: concrete.scalar(concrete1.values[concrete.values[0]]),
)

register(Ravel(concrete), lambda concrete: concrete.vector(*concrete.data))

register(
    Gamma(concrete, concrete1),
    concrete_same_length_vectors,
    lambda concrete, concrete1: row_major_gamma(concrete.data, concrete1.data),
)

# Generic indexing
register(Index(x, Index(x1, x2)), lambda x, x1, x2: Index(Concat(x1, x), x2))


register(
    Concat(vector, vector1),
    lambda vector, vector1: Vector(*vector.values, *vector1.values),
)


register(
    Equiv(concrete, concrete1),
    lambda concrete, concrete1: Scalar(vector.values == vector1.values),
)

register(
    Take(scalar, vector), lambda scalar, vector: Vector(*vector.values[: scalar.value])
)


register(
    Drop(scalar, vector), lambda scalar, vector: Vector(*vector.values[scalar.value :])
)


register(Dim(x), lambda x: Index(Vector(0), Shape(Shape(x))))


register(
    Gamma(concrete, concrete1),
    concrete_same_length_vectors,
    lambda concrete, concrete1: Concrete.scalar(
        row_major_gamma(concrete.data, concrete1.data)
    ),
)


register(AsConcrete(x), lambda x: AsConcreteWithShape(Shape(x), x))
register(
    AsConcreteWithShape(vector, x),
    lambda vector, x: AsConcreteWithValues(
        vector, *(Index(Vector(*idx), x) for idx in idx_from_shape(vector.values))
    ),
)
register(
    AsConcreteWithValues(vector, xs),
    matchpy.CustomConstraint(lambda xs: all(isinstance(x, Scalar) for x in xs)),
    lambda vector, xs: Array(vector.values, tuple(x.value for x in xs)),
)


register(
    If(concrete, thunk, thunk1),
    concrete_is_scalar,
    lambda concrete, thunk, thunk1: thunk.fn() if concrete.data[0] else thunk1.fn(),
)

register(
    And(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value and scalar1.value)
)


register(
    Add(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value + scalar1.value)
)


register(
    Shape(OuterProduct(x, binary_operation, x2)),
    lambda x, binary_operation, x2: Concat(Shape(x), Shape(x2)),
)


def outer_product_index(x, x1, binary_operation, x3):
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
    return If(
        And(IsScalar(new_left), IsScalar(new_right)),
        Thunk(lambda: binary_operation.operation(new_left, new_right)),
        Thunk(lambda: OuterProduct(new_left, binary_operation, new_right)),
    )


register(Index(x, OuterProduct(x1, binary_operation, x3)), outer_product_index)


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
