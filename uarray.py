import matchpy

replacer = matchpy.ManyToOneReplacer()


class Shape(matchpy.Operation):
    name = "ρ"
    arity = matchpy.Arity(1, True)


class PythonArray(matchpy.Symbol):
    def __init__(self, name, shape, data):
        super().__init__(name)
        self.shape = shape
        self.data = data

    @classmethod
    def vector(cls, name, *xs):
        # base x of shape(shape(shape(x))), so we don't create infinite shapes
        if xs == (1,):
            return cls._base
        return cls(name, (len(xs),), tuple(xs))

PythonArray._base = PythonArray('base_array', (1,), (1,))

python_array = matchpy.Wildcard.symbol("python_array", PythonArray)

replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(Shape(python_array)),
        lambda python_array: PythonArray.vector(
            f"${python_array.name}.shape", python_array.shape
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
        lambda El, Er: (MoAConcat(Shape(El), Shape(Er))),
    )
)

replacer.add(
    matchpy.ReplacementRule(
        matchpy.Pattern(MoAIndex(MoAConcat(i, j), MoAInnerProduct(El, op, Er))),
        lambda El, op, Er: op(MoAIndex(i, El), MoAIndex(j, Er)),
    )
)


outer_product = MoAOuterProduct(
    PythonVector([1, 2, 3]), PlusOperator, PythonVector([4, 5, 6])
)

replaced = replacer.replace(Shape(outer_product))

print(to_python_array(replaced))
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
