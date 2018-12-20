import typing
import typing_extensions

__all__ = ["Array", "Index", "Naturals"]

T = typing.TypeVar("T")
T_co = typing.TypeVar("T_co", covariant=True)


class Naturals(typing_extensions.Protocol):
    def __len__(self) -> int:
        ...

    def __getitem__(self, i: int) -> int:
        ...


class Array(typing_extensions.Protocol[T_co]):
    def __u_shape__(self) -> Naturals:
        ...

    def __u_psi__(self, indices: Naturals) -> T_co:
        ...

    def __u_mtype__(self) -> typing.Type[T_co]:
        ...


Index = typing.Callable[[Naturals], T]
