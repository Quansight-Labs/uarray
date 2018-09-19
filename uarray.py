# pylint: disable=E1120,W0108,W0621,E1121
import functools
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
xs = matchpy.Wildcard.star("xs")
xs2 = matchpy.Wildcard.star("xs2")

##
# Shape Operations
##


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


class Concat(matchpy.Operation):
    name = "++"
    infix = True
    arity = matchpy.Arity(2, True)


class Index(matchpy.Operation):
    name = "ψ"
    infix = True
    arity = matchpy.Arity(2, True)


##
# Literal arrays
##


class Scalar(matchpy.Symbol):
    """
    An array with an empty shape and a literal value.
    """

    def __init__(self, value):
        self.value = value

        super().__init__(repr(value), None)


class EmptyVector(matchpy.Symbol):
    pass


class Stack(matchpy.Operation):
    """
    An array of sub arrays each with the same shape.

    `Stack(x, *xs)` is defined when `xs` all have the shape of `x`.
    """

    arity = matchpy.Arity(1, False)
    name = "Stack"

    def __str__(self):
        value = " ".join(str(o) for o in self.operands)
        if isinstance(self.operands[0], Scalar):
            value = f"<{value}>"
        else:
            value = f"[{value}]"
        if self.variable_name:
            value = "{}: {}".format(self.variable_name, value)
        return value


scalar = matchpy.Wildcard.symbol("scalar", Scalar)
empty_vector = matchpy.Wildcard.symbol("empty_vector", EmptyVector)

register(Shape(empty_vector), lambda empty_vector: Stack(Scalar(0)))
register(Shape(scalar), lambda scalar: EmptyVector("∅"))

# Shape of Stack is number of sub arrays concatted with shape of all sub components
# we use the shape of the first one and assume all others are the same
register(
    Shape(Stack(x, xs)), lambda x, xs: Concat(Stack(Scalar(len(xs) + 1)), Shape(x))
)
register(Concat(x, empty_vector), lambda x, empty_vector: x)
register(Concat(empty_vector, x), lambda x, empty_vector: x)
register(Concat(Stack(xs), Stack(xs2)), lambda xs, xs2: Stack(*xs, *xs2))
register(Index(scalar, Stack(xs)), lambda scalar, xs: xs[scalar.value])

##
# Data Tuples
##

# Converts to and from a scalar of (shape, data), where data is nested tuples
# representing the data in the aray.


class DataTuple(typing.NamedTuple):
    shape: typing.Tuple[int, ...]
    data: typing.Any


is_data_tuple = matchpy.CustomConstraint(
    lambda scalar: isinstance(scalar.value, DataTuple)
)


class FromTuple(matchpy.Operation):
    arity = matchpy.Arity(1, True)
    name = "FromTuple"


class ToTuple(matchpy.Operation):
    arity = matchpy.Arity(1, True)
    name = "ToTuple"


class StackTuple(matchpy.Operation):
    arity = matchpy.Arity(1, False)
    name = "StackTuple"


def from_tuple(scalar):
    shape, data = scalar.value
    if not shape:
        return Scalar(data)
    dim, *rest = shape
    return Stack(*(FromTuple(Scalar((tuple(rest), data[i]))) for i in range(dim)))


register(FromTuple(scalar), from_tuple)


def to_tuple(scalar, xs):
    """
    Scalar is a data tuple and all of xs are also scalars of data tuples

    Can only pattern match on single symbol wildcard, or else we could do any number of them together
    """
    return Scalar(
        DataTuple(
            shape=(len(xs) + 1,) + scalar.value[0],
            data=tuple(x.value[1] for x in (scalar,) + xs),
        )
    )

def vector(xs):
    return FromTuple(Scalar((len(xs),), xs))

register(ToLiteralArray(scalar, x), is_data_tuple, lambda scalar, x: LiteralArray(scalar, *(Index(vector(ix), x) for ix in indices(scalar.data)))

register(
    ToTuple(scalar), lambda scalar: Scalar(DataTuple(shape=tuple(), data=scalar.value))
)
register(ToTuple(Stack(xs)), lambda xs: StackTuple(*map(ToTuple, xs)))
register(StackTuple(scalar, xs), is_data_tuple, to_tuple)


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
