import dataclasses
from .singleton import Singleton


@dataclasses.dataclass(unsafe_hash=True)
class Data(Singleton):
    val: int


@dataclasses.dataclass(unsafe_hash=True)
class DataChild(Data):
    val2: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.val2 = self.val + 1


class DataChild2(Data):
    pass


def test_data_returns_same():
    d1 = Data(1)
    d2 = Data(2)
    d3 = Data(2)

    assert d1.val == 1
    assert d2.val == 2
    assert d3.val == 2

    assert d1 is not d2
    assert d1 is not d3
    assert d2 is d3


def test_subclass_returns_same():
    d1 = DataChild(1)
    d2 = DataChild(2)
    d3 = DataChild(2)

    assert d1.val == 1
    assert d2.val == 2
    assert d3.val == 2

    assert d1.val2 == 2
    assert d2.val2 == 3
    assert d3.val2 == 3

    assert d1 is not d2
    assert d1 is not d3
    assert d2 is d3


def test_subclass_is_different():
    d1 = DataChild(1)
    d2 = DataChild2(1)

    assert d1.val == 1
    assert d2.val == 1

    assert d1 is not d2
    assert d1 != d2
