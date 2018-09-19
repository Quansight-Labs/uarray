# pylint: disable=E1120,W0108,W0621,E1121
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
x2 = matchpy.Wildcard.dot("x2")
x3 = matchpy.Wildcard.dot("x3")
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
        super().__init__(repr(value), None)


class Vector(matchpy.Symbol):
    def __init__(self, *values):
        self.values = tuple(values)
        super().__init__(f"<{' '.join(map(repr, values))}>", None)

    @property
    def length(self):
        return len(self.values)


class Array(matchpy.Symbol):
    # _base = Concrete((1,), (1,))
    def __init__(self, shape, data):
        self.shape = shape
        self.data = data

        super().__init__(f"[{' '.join(map(repr, data))}; ρ={repr(shape)}]", None)


scalar = matchpy.Wildcard.symbol("scalar", Scalar)
vector, vector1 = (
    matchpy.Wildcard.symbol("vector", Vector),
    matchpy.Wildcard.symbol("vector1", Vector),
)
array = matchpy.Wildcard.symbol("array", Array)

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
register(Index(vector, scalar), empty_vector, lambda scalar: scalar)
register(
    Index(vector, vector1),
    single_vector,
    lambda vector, vector1: Scalar(vector1.values[vector.values[0]]),
)
register(
    Index(vector, array),
    lambda vector, array: Index(Gamma(vector, Vector(array.shape)), Ravel(array)),
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


# class Concat(matchpy.Operation):
#     name = "++"
#     infix = True
#     arity = matchpy.Arity(2, True)


# replace(Index(x, Index(x2, x3)), Index(Concat(x, x2), x3))
# replace(Shape(Concat(x, xs)), Unify(Drop(Scalar(1), Shape(x)))


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

# class MoAOuterProduct(matchpy.Operation):
#     name = "·"
#     arity = matchpy.Arity(3, True)


# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Shape(MoAOuterProduct(El, op, Er))),
#         lambda El, Er: (MoAConcatVector(Shape(El), Shape(Er))),
#     )
# )

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Index(MoAConcatVector(i, j), MoAOuterProduct(El, op, Er))),
#         lambda El, op, Er: op(Index(i, El), Index(j, Er)),
#     )
# )


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
