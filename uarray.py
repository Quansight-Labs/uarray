import typing
import matchpy

replacer = matchpy.ManyToOneReplacer()


class PythonArray(matchpy.Symbol):
    def __init__(
        self, name: str, shape: typing.Tuple[int, ...], data: typing.Any
    ) -> None:
        super().__init__(name)
        self.shape = shape
        self.data = data

    @classmethod
    def vector(cls, name, *xs):
        # base x of shape(shape(shape(x))), so we don't create infinite shapes
        if xs == (1,):
            return cls._base
        return cls(name, (len(xs),), tuple(xs))

    @property
    def as_tuple(self):
        return (self.shape, self.data)

    @property
    def is_vector(self):
        return len(self.shape) == 1


PythonArray._base = PythonArray("base_array", (1,), (1,))

python_array = matchpy.Wildcard.symbol("python_array", PythonArray)


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(python_array)),
        lambda python_array: PythonArray.vector(
            f"${python_array.name}.shape", *python_array.shape
        ),
    )
)


class AddOperation(matchpy.Operation):
    name = "+"
    arity = matchpy.Arity(2, True)

a_l = matchpy.Wildcard.

replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(AddOperation(a_l, a_r))), lambda a_l: Shape(a_l)
    )
)


class Vector(matchpy.Operation):
    name = "Vec"
    arity = matchpy.Arity(0, False)


args = matchpy.Wildcard.star("args")

replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(Vector(args))),
        lambda args: PythonArray.vector("_", len(args)),
    )
)

replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(Vector(args))),
        lambda args: PythonArray.vector("_", len(args)),
    )
)


class MoAConcatVector(matchpy.Operation):
    name = "++"
    arity = matchpy.Arity(2, True)


replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(MoAConcatVector(a_l, a_r))),
        lambda a_l, a_r: PythonArray.vector(
            f"${python_array.name}.shape", *python_array.shape
        ),
    )
)


class ToPythonArray(matchpy.Operation):
    name = "ToPythonArray"
    arity = matchpy.Arity(1, True)


replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(ToPythonArray(python_array)), lambda python_array: python_array
    )
)


class MoAOuterProduct(matchpy.Operation):
    name = "·"
    arity = matchpy.Arity(3, True)


replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(MoAOuterProduct(El, op, Er))),
        lambda El, Er: (MoAConcatVector(Shape(El), Shape(Er))),
    )
)

# replacer.add(
#     matchpy.ReplacementRule(
#         matchpy.Pattern(Index(MoAConcatVector(i, j), MoAInnerProduct(El, op, Er))),
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
