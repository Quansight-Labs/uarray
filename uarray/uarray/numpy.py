from .moa import *


class Numpy(matchpy.Symbol):
    def __init__(self, code, index=()):  # , locals_):
        self.code = code
        # self.locals = locals_
        self.index = index
        super().__init__((code, index))

    def __str__(self):
        if self.index:
            return f'{self.code}[{", ".join(map(str, self.index))}]'
        return self.code


class ToNumpy(matchpy.Operation):
    name = "ToNumpy"
    arity = matchpy.Arity(1, True)


register(
    Call(Content(Numpy.w.x), Value.w.idx),
    lambda x, idx: Numpy(x.code, x.index + (idx.value,)),
)

register(Scalar(Content(Numpy.w.x)), lambda x: x)
