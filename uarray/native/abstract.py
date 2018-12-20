import typing
import dataclasses


from .typing import *
from .helpers import *

T = typing.TypeVar("T")


__all__ = ["AbstractNaturals", "AbstractArray"]


@dataclasses.dataclass
class AbstractNaturals(Naturals):
    length: int
    getitem: typing.Callable[[int], int]

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, index: int) -> int:
        return self.getitem(index)  # type: ignore

    @classmethod
    def empty(cls) -> "AbstractNaturals":
        def getitem(x: int):
            raise IndexError()

        return cls(0, getitem)

    @classmethod
    def from_value(cls, x: int) -> "AbstractNaturals":
        return cls(1, lambda _: x)

    @classmethod
    def from_array(cls, a: Array[int]) -> "AbstractNaturals":
        assert is_vector(a)
        return cls(u_shape(a)[0], lambda i: u_psi(a, cls.from_value(i)))

    @classmethod
    def from_sequence(cls, s: typing.Sequence[int]) -> "AbstractNaturals":
        return cls(len(s), s.__getitem__)


@dataclasses.dataclass
class AbstractArray(Array[T]):
    shape: Naturals
    index_fn: Index[T]
    mtype: typing.Type[T]

    def __u_shape__(self) -> Naturals:
        return self.shape

    def __u_psi__(self, indices: Naturals) -> T:
        return self.index_fn(indices)  # type: ignore

    def __u_mtype__(self) -> typing.Type[T]:
        return self.mtype

    @classmethod
    def from_value(cls, x: T, mtype: typing.Type[T] = None) -> "AbstractArray[T]":
        return AbstractArray(tuple(), lambda _: x, mtype or type(x))

    @classmethod
    def from_naturals(cls, xs: Naturals) -> "AbstractArray[int]":
        return AbstractArray((len(xs),), lambda idxs: xs[idxs[0]], int)

    @classmethod
    def from_array(cls, a: Array[T]) -> "AbstractArray[T]":
        return AbstractArray(u_shape(a), a.__u_psi__, a.__u_mtype__())

