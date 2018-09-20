# pylint: disable=E1120,W0108,W0621,E1121
"""
Guidelines:

* We want there to be only one way to compile each expression, so don't write two replacement that could apply to the same thing
  I am not sure if there is an order of preference for my specific rules
"""
import functools
import itertools
import operator
import typing

import matchpy

##
# Replacer
##
replacer = matchpy.ManyToOneReplacer()


def register(*args):
    pattern, *constraints, replacement = args
    replacer.add(
        matchpy.ReplacementRule(matchpy.Pattern(pattern, *constraints), replacement)
    )


replace = replacer.replace

##
# General wildcards
##

x = matchpy.Wildcard.dot("x")
x1 = matchpy.Wildcard.dot("x1")
x2 = matchpy.Wildcard.dot("x2")
x3 = matchpy.Wildcard.dot("x3")
x4 = matchpy.Wildcard.dot("x4")
xs = matchpy.Wildcard.star("xs")
xs2 = matchpy.Wildcard.star("xs2")

##
# Basic Operations
##


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


##
# Concrete arrays
##


class Scalar(matchpy.Symbol):
    def __init__(self, value):
        self.value = value
        super().__init__(str(value), None)

    def __repr__(self):
        return f"Scalar({repr(self.value)})"


class Vector(matchpy.Symbol):
    def __init__(self, *values):
        self.values = tuple(values)
        super().__init__(f"<{' '.join(map(repr, values))}>", None)

    @property
    def length(self):
        return len(self.values)

    def __repr__(self):
        return f"Vector({', '.join(map(repr, self.values))})"


class Array(matchpy.Symbol):
    # _base = Concrete((1,), (1,))
    def __init__(self, shape, data):
        self.shape = shape
        self.data = data

        super().__init__(f"[{' '.join(map(repr, data))}; ρ={repr(shape)}]", None)


scalar = matchpy.Wildcard.symbol("scalar", Scalar)
scalar1 = matchpy.Wildcard.symbol("scalar1", Scalar)
vector = matchpy.Wildcard.symbol("vector", Vector)
vector1 = matchpy.Wildcard.symbol("vector1", Vector)
array = matchpy.Wildcard.symbol("array", Array)


@matchpy.CustomConstraint
def scalar_true(scalar):
    return scalar.value


empty_vector = matchpy.CustomConstraint(lambda vector: vector.length == 0)

single_vector = matchpy.CustomConstraint(lambda vector: vector.length == 1)

same_length_vectors = matchpy.CustomConstraint(
    lambda vector, vector1: vector.length == vector1.length
)

scalar_array = matchpy.CustomConstraint(lambda array: array.shape == tuple())


def row_major_gamma(idx, shape):
    """
    As defined in 3.30
    """
    if not idx:
        return 0
    return idx[-1] + shape[-1] * row_major_gamma(idx[:-1], shape[:-1])


register(Shape(scalar), lambda scalar: Vector())
register(Shape(vector), lambda vector: Vector(vector.length))
register(Shape(array), lambda array: Vector(*array.shape))
register(Index(vector, scalar), empty_vector, lambda vector, scalar: scalar)
register(Index(vector, x), empty_vector, lambda vector, x: x)


def index_vectors(vector, vector1):
    return Scalar(vector1.values[vector.values[0]])


register(Index(vector, vector1), single_vector, index_vectors)
register(
    Index(vector, array),
    lambda vector, array: Index(Gamma(vector, Vector(*array.shape)), Ravel(array)),
)
register(Ravel(array), lambda array: Vector(*array.data))
register(
    Gamma(vector, vector1),
    same_length_vectors,
    lambda vector, vector1: Scalar(row_major_gamma(vector.values, vector1.values)),
)

# Why not have them all be the same?


##
# Converting to
##


class AsArray(matchpy.Operation):
    name = "AsArray"
    arity = matchpy.Arity(1, True)


class AsArrayWithShape(matchpy.Operation):
    name = "AsArrayWithShape"
    arity = matchpy.Arity(2, True)


class AsArrayWithValues(matchpy.Operation):
    name = "AsArrayWithValues"
    arity = matchpy.Arity(1, False)


def idx_from_shape(shape):
    return map(tuple, itertools.product(*map(range, shape)))


register(AsArray(x), lambda x: AsArrayWithShape(Shape(x), x))
register(
    AsArrayWithShape(vector, x),
    lambda vector, x: AsArrayWithValues(
        vector, *(Index(Vector(*idx), x) for idx in idx_from_shape(vector.values))
    ),
)
register(
    AsArrayWithValues(vector, xs),
    matchpy.CustomConstraint(lambda xs: all(isinstance(x, Scalar) for x in xs)),
    lambda vector, xs: Array(vector.values, tuple(x.value for x in xs)),
)

##
# Changing Arrays
##


class Dim(matchpy.Operation):
    name = "δ"
    arity = matchpy.Arity(1, True)


register(Dim(x), lambda x: Index(Vector(0), Shape(Shape(x))))


class Take(matchpy.Operation):
    name = "↑"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Take(scalar, vector), lambda scalar, vector: Vector(*vector.values[: scalar.value])
)


class Drop(matchpy.Operation):
    name = "↓"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Drop(scalar, vector), lambda scalar, vector: Vector(*vector.values[scalar.value :])
)


class Equiv(matchpy.Operation):
    name = "≡"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Equiv(scalar, scalar1),
    lambda scalar, scalar1: Scalar(scalar.value == scalar1.value),
)
register(
    Equiv(vector, vector1),
    lambda vector, vector1: Scalar(vector.values == vector1.values),
)


class Concat(matchpy.Operation):
    name = "‡"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Concat(vector, vector1),
    lambda vector, vector1: Vector(*vector.values, *vector1.values),
)


class IsScalar(matchpy.Operation):
    name = "IsScalar"
    arity = matchpy.Arity(1, True)


register(IsScalar(x), lambda x: Equiv(Dim(x), Scalar(0)))

##
# Logic
##


class Thunk(matchpy.Symbol):
    def __init__(self, fn):
        self.fn = fn
        super().__init__(matchpy.utils.get_short_lambda_source(fn) or repr(fn), None)


thunk = matchpy.Wildcard.symbol("thunk", Thunk)
thunk1 = matchpy.Wildcard.symbol("thunk1", Thunk)


class If(matchpy.Operation):
    name = "if"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        expr, if_true, if_false = self.operands
        return f"{expr} ? {if_true} : {if_false}"


register(
    If(scalar, thunk, thunk1),
    lambda scalar, thunk, thunk1: thunk.fn() if scalar.value else thunk1.fn(),
)

##
# Operations
##


class And(matchpy.Operation):
    name = "and"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    And(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value and scalar1.value)
)


class Add(matchpy.Operation):
    name = "+"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Add(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value + scalar1.value)
)


##
# Higher Order
##


class BinaryOperation(matchpy.Symbol):
    def __init__(self, operation):
        self.operation = operation
        super().__init__(str(operation), None)


binary_operation = matchpy.Wildcard.symbol("binary_operation", BinaryOperation)


class OuterProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"{l} ·{op} {r}"


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


def replace_debug(expr, n=10, use_repr=False):
    for i in range(n):
        print((repr if use_repr else str)(replace(expr, i)))


# class ConcatWithShapes(matchpy.Operation):
#     name = "ConcatWithShapes"
#     infix = False
#     arity = matchpy.Arity(4, True)


# def concat_shape(x, x1, x2, x3):
#     a_shape, b_shape = x1, x3
#     return Concat(
#         Add(Take(Scalar(1), a_shape), Take(Scalar(1), b_shape)),
#         Unify(Drop(Scalar(1), a_shape), Drop(Scalar(1), b_shape)),
#     )

# def concat_index(x, x1, x2, x3)

# replace(Concat(x, x1), lambda x, x1: ConcatWithShapes(Shape(x), x, Shape(x1), x1))
# replace(Shape(ConcatWithShapes(x, x1, x2, x3)), concat_shape)
# replace(Index(x4, ConcatWithShapes(x, x1, x2, x3)), concat_with_shapes)


# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Index(MoAConcatVector(i, j), MoAOuterProduct(El, op, Er))),
#         lambda El, op, Er: op(Index(i, El), Index(j, Er)),
#     )
# )

# replace(Index(x, Index(x2, x3)), Index(Concat(x, x2), x3))
#


##
# Data Operations
##


# class PythonBinaryOperator(matchpy.Symbol):
#     def __init__(self, name, operator_):
#         super().__init__(name)
#         self.operator = operator_


# class BinaryOperator(matchpy.Operation):
#     name = "BinaryOperator"
#     arity = matchpy.Arity(3, True)


# p_o = matchpy.Wildcard.symbol("python_binary_operator", PythonBinaryOperator)
# o = matchpy.Wildcard.dot("o")

# a = matchpy.Wildcard.dot("a")
# a_l = matchpy.Wildcard.dot("a_l")
# a_r = matchpy.Wildcard.dot("a_r")
# v = matchpy.Wildcard.dot("v")

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Shape(BinaryOperator(o, a_l, a_r))), lambda a_l: Shape(a_l)
#     )
# )


# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Index(v, BinaryOperator(o, a_l, a_r))),
#         lambda v, a_l, a_r: BinaryOperator(o, Index(v, a_l), Index(v, a_r)),
#     )
# )
# python_array_l = matchpy.Wildcard.symbol("python_array_l", PythonArray)
# python_array_l_is_scalar = matchpy.CustomConstraint(
#     lambda python_array_l: python_array_l.is_scalar
# )

# python_array_r = matchpy.Wildcard.symbol("python_array_r", PythonArray)
# python_array_r_is_scalar = matchpy.CustomConstraint(
#     lambda python_array_r: python_array_r.is_scalar
# )

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(
#             BinaryOperator(p_o, python_array_l, python_array_r),
#             python_array_l_is_scalar,
#             python_array_r_is_scalar,
#         ),
#         lambda p_o, python_array_l, python_array_r: PythonArray(
#             None, tuple(), p_o.operator(python_array_l.data, python_array_r.data)
#         ),
#     )
# )


# class Vector(matchpy.Operation):
#     name = "Vector"
#     arity = matchpy.Arity(0, False)


# args = matchpy.Wildcard.star("args")

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Shape(Vector(args))),
#         lambda args: PythonArray.vector("_", len(args)),
#     )
# )

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Shape(Vector(args))),
#         lambda args: PythonArray.vector("_", len(args)),
#     )
# )


# class If(matchpy.Operation):
#     name = "if"
#     arity = matchpy.Arity(3, True)


# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(If(python_array, a_l, a_r), python_array_is_scalar),
#         lambda python_array, a_l, a_r: a_l if python_array.data else a_r,
#     )
# )


# AddOperator = functools.partial(
#     BinaryOperator, PythonBinaryOperator("add", operator.add)
# )

# LessEqualOperator = functools.partial(
#     BinaryOperator, PythonBinaryOperator("<=", operator.le)
# )


# class MoAConcatVector(matchpy.Operation):
#     name = "++"
#     arity = matchpy.Arity(2, True)


# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Shape(MoAConcatVector(a_l, a_r))),
#         lambda a_l, a_r: AddOperator(Shape(a_l), Shape(a_r)),
#     )
# )

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Index(Vector(a), MoAConcatVector(a_l, a_r))),
#         lambda a, a_l, a_r: If(LessEqualOperator()),
#     )
# )


# class ToPythonArray(matchpy.Operation):
#     name = "ToPythonArray"
#     arity = matchpy.Arity(2, True)


# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(ToPythonArray(literal_vector, python_array)),
#         lambda python_array: python_array,
#     )
# )

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(ToPythonArray(literal_vector, array)),
#         lambda python_array: python_array,
#     )
# )

# replacer.matcher.as_graph().view()


# outer_product = MoAOuterProduct(
#     PythonVector([1, 2, 3]), PlusOperator, PythonVector([4, 5, 6])
# )


# print(to_python_array(replaced))
# class MoAInnerProduct(matchpy.Operation):
#     name = '·'
#     arity = matchpy.Arity(4, True)

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Shape(MoAInnerProduct(El, op1, op2, Er))),
#         lambda El, Er: (MoAConcat(MoADrop(-1, Shape(El)), MoADrop(1, Shape(Er))))
#     )
# )

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(MoAIndex(MoAConcat(i, j), MoAInnerProduct(El, op, Er))),
#         lambda El, op, Er: op(MoAIndex(i, El), MoAIndex(j, Er))
#     )
# )


## old


# class EmptyVector(matchpy.Symbol):
#     pass


# class BaseShape(matchpy.Symbol):
#     """
#     <1>

#     Only array with the shape equal to itself,
#     useful as a singleton for the base case of Shape definitions
#     """

#     pass


# empty_vector = matchpy.Wildcard.symbol("empty_vector", EmptyVector)
# base_shape = matchpy.Wildcard.symbol("base_shape", BaseShape)


# register(Shape(empty_vector), lambda: ArrayElements(empty_vector, Scalar(0)))
