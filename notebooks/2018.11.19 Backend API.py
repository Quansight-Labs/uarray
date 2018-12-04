import typing
import typing_extensions
from uarray import *
from dataclasses import dataclass
#%% [markdown]
# Let's look at some examples of different frontend APIs:


#%%

T_contra = typing.TypeVar("T_contra", contravariant=True)
T_co = typing.TypeVar("T_co", covariant=True)

# Sequences

class SequenceBackendRetT(typing.NamedTuple):
    create: typing.Callable[[CContent], CNestedSequence]
    setitem: typing.Callable[[CNestedSequence, CContent, T], None]

class SequenceBackendRet(typing_extensions.Protocol[T_contra]):
    value: CNestedSequence

    def __init__(self, length: CContent) -> None:
        ...

    def __setitem__(self, index: CContent, value: T_contra) -> None:
        ...


class ListBackendRet(SequenceBackendRet[T_contra]):
    def __init__(self, length: CContent) -> None:
        self.value = [] 

class SequenceBackendArg(typing_extensions.Protocol[T_co]):
    def __getitem__(self, index: CContent) -> T_co:
        ...

    def __len__(self) -> CContent:
        ...


# ND Arrays


class NDArrayBackendRet(typing_extensions.Protocol[T_contra]):
    def __init__(self, shape: CVectorCallable[CContent]) -> None:
        ...

    def __setitem__(self, indices: CVectorCallable[CContent], value: T_contra) -> None:
        ...


class NDArrayBackendArg(typing_extensions.Protocol[T_co]):
    def __getitem__(self, indices: CVectorCallable[CContent]) -> T_co:
        ...

    def __shape__(self) -> CVectorCallable[CContent]:
        ...


# class ContentBackend(typing_extensions.Protocol[T_contra]):
#     def __add__(self, )