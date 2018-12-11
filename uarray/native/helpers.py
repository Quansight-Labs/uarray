import typing

from .typing import *

__all__ = ["u_shape", "u_psi", "u_mtype", "is_scalar", "is_vector"]
T = typing.TypeVar("T")


def u_shape(a: Array[T]) -> Naturals:
    return a.__u_shape__()


def u_psi(a: Array[T], indices: Naturals) -> T:
    return a.__u_psi__(indices)


def u_mtype(a: Array[T]) -> typing.Type[T]:
    return a.__u_mtype__()


def is_scalar(a: Array[T]):
    return len(u_shape(a)) == 0


def is_vector(a: Array[T]):
    return len(u_shape(a)) == 1
