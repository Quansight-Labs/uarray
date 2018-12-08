import pytest

from uarray.parser import build_parser
from uarray import moa, core


@pytest.mark.parametrize("expression,result", [
    ("< 1 2 3>", core.vector(1, 2, 3)),
    ('j', core.unbound('j')),
    ## Enable these tests once PR is merged
    ## https://github.com/Quansight-Labs/uarray/pull/73
    # ('j ^ <1 2>', core.with_shape(core.unbound('j'), core.vector(1, 2))),
    # ('j ^ <1 2> + <3 4>',
    #  moa.Add(
    #      core.with_shape(core.unbound('j'), core.vector(1, 2)),
    #      core.vector(3, 4))),
    ("j psi x",
     moa.Index(
         core.unbound('j'),
         core.unbound('x'))),
    ("<1 2> + <2 3>",
     moa.Add(
         core.vector(1, 2),
         core.vector(2, 3))),
    ("<1 2> + (A  * <2 3>)",
     moa.Add(
         core.vector(1, 2),
         moa.Multiply(
             core.unbound('A'),
             core.vector(2, 3)))),
    ("<1 2> + A * <2 3>",
     moa.Add(
         core.vector(1, 2),
         moa.Multiply(
             core.unbound('A'),
             core.vector(2, 3)))),
    ("A + B + C",
     moa.Add(
         moa.Add(
             core.unbound('A'),
             core.unbound('B')),
         core.unbound('C'))),
])
def test_parse_expression(expression, result):
    parser = build_parser()
    parser_result = parser.parse(expression)
    print('parsed:', parser_result)
    print('expected:', result)
    assert parser_result == result
