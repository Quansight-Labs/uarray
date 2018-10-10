# pylint: disable=E1120,W0108,W0621,E1121,E1101
"""

"""
import itertools
import pprint
import typing

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


##
# Utils
##


# def product(xs):
#     r = 1
#     for x_ in xs:
#         r *= x_
#     return r


# def idx_from_shape(shape):
#     return map(tuple, itertools.product(*map(range, shape)))


# def row_major_gamma(idx, shape):
#     """
#     As defined in 3.30
#     """
#     assert len(idx) == len(shape)
#     if not idx:
#         return 0
#     assert idx < shape
#     return idx[-1] + (shape[-1] * row_major_gamma(idx[:-1], shape[:-1]))


# def row_major_gamma_inverse(n, shape):
#     """
#     As defined in 3.41
#     """
#     assert n >= 0
#     assert n < product(shape)
#     for x_ in shape:
#         assert x_ > 0

#     if len(shape) == 1:
#         return (n,)

#     *next_shape, dim = shape
#     return (*row_major_gamma_inverse(n // dim, next_shape), n % dim)


##


x = matchpy.Wildcard.dot("x")
x1 = matchpy.Wildcard.dot("x1")
x2 = matchpy.Wildcard.dot("x2")
x3 = matchpy.Wildcard.dot("x3")
x4 = matchpy.Wildcard.dot("x4")

xs = matchpy.Wildcard.star("xs")
xs1 = matchpy.Wildcard.star("xs1")

# Everything (Operations and Symbols) are one of two types:
#
# Arrays: Reduce down to Array(length: Accessor, content: Accessor)
# Accessors: Accessors support calling Get(index: Accessor, content: Accessor) -> Array


class Array(matchpy.Operation):
    """
    Array(length, content)
    """

    name = "Array"
    arity = matchpy.Arity(2, True)

    # def __str__(self):
    #     return f"Array({str(self.operands[1])}, l={self.operands[0]})"


class Get(matchpy.Operation):
    """
    Get(index, content)
    """

    name = "Get"
    arity = matchpy.Arity(2, True)


# What about scalars? Those are also Arrays, but with length of NoLengthAccessor
class NoLengthAccessor(matchpy.Operation):
    name = "NoLengthAccessor"
    arity = matchpy.Arity(0, True)


class ScalarAccessor(matchpy.Symbol):
    def __init__(self, value):
        self.value = value
        super().__init__(repr(value), None)

    def __str__(self):
        return str(self.value)


scalar_accessor = matchpy.Wildcard.symbol("scalar_accessor", ScalarAccessor)
scalar_accessor_1 = matchpy.Wildcard.symbol("scalar_accessor_1", ScalarAccessor)
scalar_accessor_2 = matchpy.Wildcard.symbol("scalar_accessor_2", ScalarAccessor)


def scalar(value):
    return Array(NoLengthAccessor(), ScalarAccessor(value))


class VectorAccessor(matchpy.Symbol):
    def __init__(self, items):
        for i in items:
            assert isinstance(i, matchpy.Expression)
        self.items = items
        super().__init__(repr(items), None)

    def __str__(self):
        return f"<{' '.join(map(str, self.items))}>"


def vector(*values):
    accessor = VectorAccessor(tuple(ScalarAccessor(v) for v in values))
    return Array(ScalarAccessor(len(values)), accessor)


vector_accessor = matchpy.Wildcard.symbol("vector_accessor", VectorAccessor)


class VectorAccessorGetContents(matchpy.Operation):
    name = "VectorAccessorGetContents"
    arity = matchpy.Arity(2, True)


register(
    VectorAccessorGetContents(scalar_accessor, vector_accessor),
    lambda scalar_accessor, vector_accessor: vector_accessor.items[
        scalar_accessor.value
    ],
)

register(
    Get(x, vector_accessor),
    lambda x, vector_accessor: Array(
        NoLengthAccessor(),
        # defer getting contents to new operation which is just defined for
        VectorAccessorGetContents(x, vector_accessor),
    ),
)


# What about accessor that we don't know the value of at compile time?
class UnboundAccessor(matchpy.Symbol):
    def __init__(self, variable_name=None):
        super().__init__(name="", variable_name=variable_name)

    def __str__(self):
        return f"UnboundAccessor({self.variable_name or '' })"


register(Get(x, scalar_accessor), lambda x, scalar_accessor: vector())


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


class ShapeInner(matchpy.Operation):
    """
    ShapeInner(current_shape: Scalar[Tuple[int, ...]], next_dim_array: Array)
    """

    name = "ShapeInner"
    arity = matchpy.Arity(2, True)


def _shape_inner(scalar_accessor, x, x1):
    current_shape: typing.Tuple[int, ...] = scalar_accessor.value
    # If there is no length here, we are at a scalar dimension, so return what we have
    if isinstance(x, NoLengthAccessor):
        return vector(*current_shape)
    # otherwise get the next dimension
    new_shape = current_shape + (x,)
    return ShapeInner(ScalarAccessor(new_shape), Get(UnboundAccessor(), x1))


register(
    Shape(Array(x, x1)), lambda x, x1: ShapeInner(ScalarAccessor(tuple()), Array(x, x1))
)

register(ShapeInner(scalar_accessor, Array(x, x1)), _shape_inner)


class Index(matchpy.Operation):
    name = "ψ"
    infix = True
    arity = matchpy.Arity(2, True)


def _index(idx_length, idx_content, array):
    for i in range(idx_length):
        index_value = Get(ScalarAccessor(i), idx_content)
        array = Get(Content(index_value), Content(array))
    return array


register(
    Index(Array(scalar_accessor, x), x1),
    lambda scalar_accessor, x, x1: _index(scalar_accessor.value, x, x1),
)


class Content(matchpy.Operation):
    name = "Content"
    arity = matchpy.Arity(1, True)


register(Content(Array(x, x1)), lambda x, x1: x1)


class Apply(matchpy.Operation):
    """
    Apply(x, xs) -> calls operation x with args xs 
    """

    name = "Apply"
    arity = matchpy.Arity(1, False)


register(
    Apply(scalar_accessor, xs), lambda scalar_accessor, xs: scalar_accessor.value(*xs)
)


class ReduceVector(matchpy.Operation):
    """
    ReduceVector(initial_value, operation, a: Array)
    """

    name = "red"
    arity = matchpy.Arity(3, True)


class ReduceVectorInner(matchpy.Operation):
    """
    ReduceVectorInner(current_idx, current_value, operation, a: Array)
    """

    name = "ReduceVectorInner"
    arity = matchpy.Arity(4, True)


register(
    ReduceVector(x, x1, x2),
    lambda x, x1, x2: ReduceVectorInner(ScalarAccessor(0), x, x1, x2),
)


def _reduce_vector_inner(scalar_accessor, x, x1, scalar_accessor_1, x3):
    current_idx = scalar_accessor
    current_value = x
    operation = x1
    vector_length = scalar_accessor_1
    vector_content = x3

    # if we have gone all the way through the vector return the reduced value
    if current_idx.value == vector_length.value:
        return current_value

    next_value = Apply(operation, current_value, Get(current_idx, vector_content))
    return ReduceVectorInner(
        ScalarAccessor(current_idx.value + 1),
        next_value,
        operation,
        Array(vector_length, vector_content),
    )


register(
    ReduceVectorInner(scalar_accessor, x, x1, Array(scalar_accessor_1, x3)),
    _reduce_vector_inner,
)


class Add(matchpy.Operation):
    name = "+"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Add(
        Array(NoLengthAccessor(), scalar_accessor),
        Array(NoLengthAccessor(), scalar_accessor_1),
    ),
    lambda scalar_accessor, scalar_accessor_1: Array(
        NoLengthAccessor(),
        ScalarAccessor(scalar_accessor.value + scalar_accessor_1.value),
    ),
)


class Multiply(matchpy.Operation):
    name = "*"
    infix = True
    arity = matchpy.Arity(2, True)


register(
    Multiply(
        Array(NoLengthAccessor(), scalar_accessor),
        Array(NoLengthAccessor(), scalar_accessor_1),
    ),
    lambda scalar_accessor, scalar_accessor_1: Array(
        NoLengthAccessor(),
        ScalarAccessor(scalar_accessor.value * scalar_accessor_1.value),
    ),
)


class Pi(matchpy.Operation):
    name = "π"
    arity = matchpy.Arity(1, True)


register(Pi(x), lambda x: ReduceVector(scalar(1), ScalarAccessor(Multiply), x))


class Total(matchpy.Operation):
    name = "τ"
    arity = matchpy.Arity(1, True)


register(Total(x), lambda x: Pi(Shape(x)))


class GetBySubstituting(matchpy.Operation):
    """
    GetBySubstituting(variable_name, form)
    """

    name = "GetBySubstituting"
    arity = matchpy.Arity(2, True)


register(
    Get(x, GetBySubstituting(scalar_accessor, x1)),
    lambda x, scalar_accessor, x1: matchpy.substitute(x1, {scalar_accessor.value: x}),
)

_counter = 0


def get_index_accessor():
    """
    Returns index variable and fn of array -> GetBySubstituting 
    """
    global _counter
    variable_name = f"idx_{_counter}"
    _counter += 1
    idx_variable = UnboundAccessor(variable_name=variable_name)
    return (
        idx_variable,
        lambda a, variable_name=variable_name: GetBySubstituting(
            ScalarAccessor(variable_name), a
        ),
    )


def with_get(fn):
    """
    with_get(fn: index accessor -> Array)
    """
    idx_variable, creator = get_index_accessor()
    return creator(fn(idx_variable))


class Iota(matchpy.Operation):
    """
    Iota(n) returns a vector of 0 to n-1.
    """

    name = "ι"
    arity = matchpy.Arity(1, True)


register(
    Iota(Array(NoLengthAccessor(), scalar_accessor)),
    lambda scalar_accessor: Array(
        scalar_accessor, with_get(lambda idx: Array(NoLengthAccessor(), idx))
    ),
)


class Dim(matchpy.Operation):
    """
    Dimensionality
    """

    name = "δ"
    arity = matchpy.Arity(1, True)


register(Dim(x), lambda x: Pi(Shape(Shape(x))))


class AbstractWithDimension(matchpy.Symbol):
    def __init__(self, n, variable_name):
        self.n = n
        super().__init__(str(n), variable_name)

    def __str__(self):
        return f"{self.variable_name}^{self.n}"


abstract_with_dimension = matchpy.Wildcard.symbol(
    "abstract_with_dimension", AbstractWithDimension
)


def _abstract_with_dimension_inner(shape, content, n_dim, i=0):
    if i == n_dim:
        return Array(NoLengthAccessor(), content)

    return Array(
        Content(Get(ScalarAccessor(i), shape)),
        with_get(
            lambda idx: _abstract_with_dimension_inner(
                shape=shape, content=Content(Get(idx, content)), n_dim=n_dim, i=i + 1
            )
        ),
    )


register(
    abstract_with_dimension,
    lambda abstract_with_dimension: _abstract_with_dimension_inner(
        UnboundAccessor(variable_name=f"{abstract_with_dimension.variable_name}_shape"),
        UnboundAccessor(
            variable_name=f"{abstract_with_dimension.variable_name}_content"
        ),
        abstract_with_dimension.n,
    ),
)


class BinaryOperation(matchpy.Operation):
    name = "BinaryOperation"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"({l} {op.value} {r})"


def _binary_operation(x, x1, x2, x3, x4):
    l_length, l_content = x, x1
    op = x2
    r_length, r_content = x3, x4
    l, r = Array(l_length, l_content), Array(r_length, r_content)

    l_is_scalar = isinstance(l_length, NoLengthAccessor)
    r_is_scalar = isinstance(r_length, NoLengthAccessor)

    if l_is_scalar and r_is_scalar:
        return Apply(op, l, r)
    if l_is_scalar:
        return Array(
            r_length, with_get(lambda idx: BinaryOperation(l, op, Get(idx, r_content)))
        )
    if r_is_scalar:
        return Array(
            l_length, with_get(lambda idx: BinaryOperation(Get(idx, l_content), op, r))
        )
    assert l_length == r_length
    return Array(
        l_length,
        with_get(
            lambda idx: BinaryOperation(Get(idx, l_content), op, Get(idx, r_content))
        ),
    )


register(BinaryOperation(Array(x, x1), x2, Array(x3, x4)), _binary_operation)


class OuterProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(3, True)

    def __str__(self):
        l, op, r = self.operands
        return f"({l} ·{op} {r})"


def _outer_product(x, x1, x2, x3, x4):
    l_length, l_content = x, x1
    op = x2
    r_length, r_content = x3, x4
    l, r = Array(l_length, l_content), Array(r_length, r_content)

    l_is_scalar = isinstance(l_length, NoLengthAccessor)
    if l_is_scalar:
        return BinaryOperation(l, op, r)

    return Array(
        l_length, with_get(lambda idx: OuterProduct(Get(idx, l_content), op, r))
    )


register(OuterProduct(Array(x, x1), x2, Array(x3, x4)), _outer_product)


class InnerProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(4, True)

    def __str__(self):
        l, op_l, op_r, r = self.operands
        return f"({l} {op_l}·{op_r} {r})"


def scalar_accessor_is(x, prefix=""):
    return matchpy.CustomConstraint(lambda y: y.value == x).with_renamed_vars(
        {"y": f"scalar_accessor_{prefix}"}
    )


# inner product is associative with scalar multiplication
# TODO: Make this commutative so works for other orders of inner product and binary op.
register(
    InnerProduct(
        x,
        scalar_accessor,
        scalar_accessor_1,
        BinaryOperation(Array(NoLengthAccessor(), x1), scalar_accessor_2, x2),
    ),
    scalar_accessor_is(Add),
    scalar_accessor_is(Multiply, "_1"),
    scalar_accessor_is(Multiply, "_2"),
    lambda x, scalar_accessor, scalar_accessor_1, x1, scalar_accessor_2, x2: BinaryOperation(
        Array(NoLengthAccessor(), x1),
        scalar_accessor_2,
        InnerProduct(x, scalar_accessor, scalar_accessor_1, x2),
    ),
)


# class NumpyCodeStringAccessor(matchpy.Symbol):
#     def __init__(self, code):
#         self.code = code
#         super().__init__(repr(code), None)

#     def __str__(self):
#         return f"NP({self.code})"


# register()

# class Reshape(matchpy.Operation):
#     name = "ρ"
#     arity = matchpy.Arity(2, True)
#     infix = True


# class ReshapeVector(matchpy.Operation):
#     """
#     Reshape where we know the array is a vector
#     """

#     name = "ρ"
#     arity = matchpy.Arity(2, True)
#     infix = True


# class If(matchpy.Operation):
#     name = "if"
#     arity = matchpy.Arity(3, True)

#     def __str__(self):
#         expr, if_true, if_false = self.operands
#         return f"({expr} ? {if_true} : {if_false})"


# class Ravel(matchpy.Operation):
#     name = "rav"
#     arity = matchpy.Arity(1, True)


# class RavelArray(matchpy.Operation):
#     """
#     Ravel where dim array > 1
#     """

#     name = "rav-a"
#     arity = matchpy.Arity(1, True)


# class Gamma(matchpy.Operation):
#     name = "γ"
#     arity = matchpy.Arity(2, True)


# class GammaInverse(matchpy.Operation):
#     name = "γ'"
#     arity = matchpy.Arity(2, True)


# class And(matchpy.Operation):
#     """
#     And(first, lambda: second)
#     """

#     name = "and"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class Not(matchpy.Operation):
#     name = "not"
#     arity = matchpy.Arity(1, True)


# class Mod(matchpy.Operation):
#     name = "mod"
#     arity = matchpy.Arity(2, True)


# class Add(matchpy.Operation):
#     name = "+"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class Multiply(matchpy.Operation):
#     name = "×"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class Abs(matchpy.Operation):
#     name = "abs"
#     arity = matchpy.Arity(1, True)


# class Subtract(matchpy.Operation):
#     name = "-"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class LessThen(matchpy.Operation):
#     name = "<"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class Dim(matchpy.Operation):
#     """
#     Dimensionality
#     """

#     name = "δ"
#     arity = matchpy.Arity(1, True)


# class Take(matchpy.Operation):
#     name = "↑"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class Drop(matchpy.Operation):
#     """
#     Drop(vector, array)
#     """

#     name = "↓"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class Equiv(matchpy.Operation):
#     name = "≡"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class EquivArray(matchpy.Operation):
#     """
#     EquivArray(dim_l, dim_r, l, r)
#     """

#     name = "≡a"
#     infix = True
#     arity = matchpy.Arity(4, True)

#     def __str__(self):
#         d_l, d_r, l, r = self.operands
#         return f"({l}^{d_l} ≡a {r}^{d_l})"


# class EquivScalar(matchpy.Operation):
#     name = "≡s"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class ConcatVector(matchpy.Operation):
#     name = "‡v"
#     infix = True
#     arity = matchpy.Arity(2, True)


# class BinaryOperation(matchpy.Operation):
#     name = "BinaryOperation"
#     arity = matchpy.Arity(3, True)

#     def __str__(self):
#         l, op, r = self.operands
#         return f"({l} {op.value} {r})"


# class BinaryOperationScalarExtension(matchpy.Operation):
#     name = "BinaryOperationScalarExtension"
#     arity = matchpy.Arity(3, True)


# class BinaryOperationArray(matchpy.Operation):
#     name = "BinaryOperationArray"
#     arity = matchpy.Arity(3, True)


# class InnerProduct(matchpy.Operation):
#     name = "·"
#     arity = matchpy.Arity(4, True)

#     def __str__(self):
#         l, op_l, op_r, r = self.operands
#         return f"({l} {op_l}·{op_r} {r})"


# ##
# # Macros
# ##


# def vector(*values):
#     return Vector(*map(Scalar, values))


# def is_scalar(expr):
#     return EquivScalar(Dim(expr), Scalar(0), variable_name="is_scalar")


# def is_vector(expr):
#     return EquivScalar(Dim(expr), Scalar(1), variable_name="is_vector")


# def add(l, r):
#     return BinaryOperation(l, Scalar(Add), r)


# def vector_first(expr):
#     return FullIndex(vector(0), expr)


# ##
# # Wildcards
# ##

# scalar = matchpy.Wildcard.symbol("scalar", Scalar)
# scalar1 = matchpy.Wildcard.symbol("scalar1", Scalar)
# scalar2 = matchpy.Wildcard.symbol("scalar2", Scalar)


# ##
# # Constraints
# ##
# xs_are_scalars = matchpy.CustomConstraint(
#     lambda xs: all(isinstance(x_, Scalar) for x_ in xs)
# )
# xs1_are_scalars = matchpy.CustomConstraint(
#     lambda xs1: all(isinstance(x_, Scalar) for x_ in xs1)
# )

# ##
# # Replacements
# ##

# # Abstract
# register(Shape(Shape(AbstractWithDimension(x))), lambda x: Vector(x))

# # Scalar replacements
# register(Shape(scalar), lambda scalar: vector())
# register(Not(scalar), lambda scalar: Scalar(not scalar.value))
# register(Abs(scalar), lambda scalar: Scalar(abs(scalar.value)))
# register(
#     And(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value and scalar1.value)
# )
# register(
#     LessThen(scalar, scalar1),
#     lambda scalar, scalar1: Scalar(scalar.value < scalar1.value),
# )
# register(
#     Mod(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value % scalar1.value)
# )

# register(
#     Add(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar.value + scalar1.value)
# )
# register(
#     Subtract(scalar, scalar1),
#     lambda scalar, scalar1: Scalar(scalar.value - scalar1.value),
# )
# register(If(scalar, x, x1), lambda scalar, x, x1: x if scalar.value else x1)
# register(
#     EquivScalar(scalar, scalar1),
#     lambda scalar, scalar1: Scalar(scalar.value == scalar1.value),
# )

# # Vector replacements
# register(Shape(Vector(xs)), lambda xs: vector(len(xs)))
# register(FullIndex(Vector(scalar), Vector(xs)), lambda scalar, xs: xs[scalar.value])
# register(
#     Gamma(Vector(xs), Vector(xs1)),
#     xs_are_scalars,
#     xs1_are_scalars,
#     lambda xs, xs1: Scalar(
#         row_major_gamma([x_.value for x_ in xs], [x_.value for x_ in xs1])
#     ),
# )
# register(
#     GammaInverse(scalar, Vector(xs)),
#     xs_are_scalars,
#     lambda scalar, xs: vector(
#         *row_major_gamma_inverse(scalar.value, [x_.value for x_ in xs])
#     ),
# )

# # dim && shape && contents are the same
# register(
#     Equiv(x, x1),
#     lambda x, x1: And(
#         EquivScalar(Dim(x), Dim(x1)),
#         And(
#             EquivArray(Scalar(1), Scalar(1), Shape(x), Shape(x1)),
#             EquivArray(Dim(x), Dim(x1), x, x1),
#         ),
#     ),
# )


# def _abstract_vector(prefix_name, length):
#     return Vector(
#         *(
#             AbstractWithDimension(Scalar(0), variable_name=f"{prefix_name}_{i}")
#             for i in range(length)
#         )
#     )


# # Contents are the same if fully indexing both result in equiv scalars
# register(
#     EquivArray(scalar, scalar1, x, x1),
#     lambda scalar, scalar1, x, x1: EquivScalar(
#         FullIndex(_abstract_vector("_equiv", scalar.value), x),
#         FullIndex(_abstract_vector("_equiv", scalar1.value), x1),
#     ),
# )

# # two scalars are equivalent if their forms are the same
# register(
#     EquivScalar(x, x1),
#     matchpy.EqualVariablesConstraint("x", "x1"),
#     lambda x, x1: Scalar(True),
# )

# # we know if they are equivalent if both are scalars
# register(
#     EquivScalar(scalar, scalar1), lambda scalar, scalar1: Scalar(scalar == scalar1)
# )

# # Also if we are comparing two concrete vectors indexed abstractly
# # we know if they are not equal if their forms are not equal
# register(
#     EquivScalar(
#         Index(Vector(AbstractWithDimension(x)), Vector(xs)),
#         Index(Vector(AbstractWithDimension(x1)), Vector(xs1)),
#     ),
#     xs_are_scalars,
#     xs1_are_scalars,
#     matchpy.EqualVariablesConstraint("x", "x1"),
#     lambda x, x1, xs, xs1: Scalar(xs == xs1),
# )

# register(
#     Pi(Vector(xs)), xs_are_scalars, lambda xs: Scalar(product(x_.value for x_ in xs))
# )

# # Generic definitions


# def reshape(x, x1):
#     """
#     TODO: Handle if x has zero, then return empty array
#     """
#     return If(is_vector(x), ReshapeVector(x, x1), ReshapeVector(x, Ravel(x1)))


# register(Reshape(x, x1), reshape)


# register(Shape(ReshapeVector(x, x1)), lambda x, x1: x)

# register(
#     FullIndex(x, ReshapeVector(x1, x2)),
#     lambda x, x1, x2: FullIndex(Vector(Mod(Gamma(x, x1), Total(x2))), x2),
# )


# register(
#     Ravel(x), lambda x: If(is_scalar(x), Vector(x), If(is_vector(x), x, RavelArray(x)))
# )


# register(
#     FullIndex(x, RavelArray(x1)),
#     lambda x, x1: FullIndex(GammaInverse(vector_first(x), Shape(x1)), x1),
# )


# register(Shape(BinaryOperationArray(x, scalar, x1)), lambda x, scalar, x1: Shape(x))
# register(
#     FullIndex(x, BinaryOperationArray(x1, scalar, x2)),
#     lambda x, x1, scalar, x2: BinaryOperation(
#         FullIndex(x, x1), scalar, FullIndex(x, x2)
#     ),
# )
# register(
#     Shape(BinaryOperationScalarExtension(x, scalar, x1)),
#     lambda x, scalar, x1: Shape(x1),
# )
# register(
#     FullIndex(x, BinaryOperationScalarExtension(x1, scalar, x2)),
#     lambda x, x1, scalar, x2: BinaryOperation(x1, scalar, FullIndex(x, x2)),
# )

# register(Shape(ConcatVector(x, x1)), lambda x, x1: add(Shape(x), Shape(x1)))


# def _index_concat_vector(x, x1, x2):
#     idx = vector_first(x)
#     size_first = vector_first(Shape(x1))
#     modified_index = Subtract(idx, size_first)
#     return If(
#         LessThen(idx, size_first), FullIndex(x, x1), FullIndex(modified_index, x2)
#     )


# register(Shape(ConcatVector(x, x1)), lambda x, x1: add(Shape(x), Shape(x1)))
# register(FullIndex(x, ConcatVector(x1, x2)), _index_concat_vector)

# register(Shape(Iota(x)), lambda x: Vector(x))
# register(FullIndex(x, Iota(x1)), lambda x, x1: vector_first(x))

# # Only vectors
# register(Shape(Take(x, x1)), lambda x, x1: Vector(Abs(vector_first(x))))
# register(
#     FullIndex(x, Take(x1, x2)),
#     lambda x, x1, x2: If(
#         LessThen(vector_first(x1), Scalar(0)),
#         FullIndex(Vector(Add(Add(Total(x2), x1), vector_first(x))), x2),
#         FullIndex(x, x2),
#     ),
# )
# register(
#     Shape(Drop(x, x1)), lambda x, x1: Vector(Subtract(Total(x1), Abs(vector_first(x))))
# )
# register(
#     FullIndex(x, Drop(x1, x2)),
#     lambda x, x1, x2: If(
#         LessThen(vector_first(x1), Scalar(0)),
#         FullIndex(x, x2),
#         FullIndex(Vector(Add(x1, vector_first(x))), x2),
#     ),
# )


# # full indexing is if shape of index is == shape of shape of value
# register(
#     Index(x, x1),
#     lambda x, x1: If(
#         EquivScalar(Total(x), Dim(x1)), FullIndex(x, x1), PartialIndex(x, x1)
#     ),
# )


# # register(Shape(Index(x, x1)), lambda x, x1: Drop(Vector(Total(x)), Shape(x1)))
# register(Shape(FullIndex(x, x1)), lambda x, x1: vector())
# register(Shape(PartialIndex(x, x1)), lambda x, x1: Drop(Vector(Total(x)), Shape(x1)))
# register(
#     PartialIndex(x, PartialIndex(x1, x2)),
#     lambda x, x1, x2: Index(ConcatVector(x1, x), x2),
# )
