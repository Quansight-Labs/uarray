import dataclasses
import typing
import abc
import functools
import operator

import typing_extensions

T = typing.TypeVar("T")
U = typing.TypeVar("U")
V = typing.TypeVar("V")


# Need this so that function attributes are not typed as methods
# https://github.com/python/mypy/issues/5485#issuecomment-441935633
@dataclasses.dataclass
class Box(typing.Generic[T]):
    inner: T

    @property
    def unboxed(self) -> T:
        return self.inner


@dataclasses.dataclass
class Always(typing.Generic[T]):
    value: T

    def __call__(self, *args, **kwargs) -> T:
        return self.value


@dataclasses.dataclass
class Compose(typing.Generic[T, U, V]):
    left: Box[typing.Callable[[U], V]]
    right: Box[typing.Callable[[T], U]]

    def __call__(self, arg: T) -> V:
        return self.left.unboxed(self.right.unboxed(arg))


class ArrayProtocol(typing_extensions.Protocol[T]):
    @abc.abstractmethod
    def __array_shape__(self) -> "VectorProtocol[int]":
        ...

    @abc.abstractmethod
    def __array_index__(self) -> "ArrayIndexProtocol[T]":
        ...


class ArrayIndexProtocol(typing_extensions.Protocol[T]):
    @abc.abstractmethod
    def __call__(self, indices: "VectorProtocol[int]") -> "ArrayProtocol[T]":
        ...


@dataclasses.dataclass
class Array(ArrayProtocol[T]):
    shape: "VectorProtocol[int]"
    index: "ArrayIndexProtocol[T]"

    def __array_shape__(self) -> "VectorProtocol[int]":
        return self.shape

    def __array_index__(self) -> ArrayIndexProtocol[T]:
        return self.index


# @dataclasses.dataclass
class EmptyArray(ArrayProtocol[T]):
    def __array__shape__(self):
        return SequenceVector([0])

    def __array_index__(self):
        return Always(EmptyArray())


class ScalarProtocol(ArrayProtocol[T], typing_extensions.Protocol):
    @abc.abstractmethod
    def __scalar_content__(self) -> T:
        ...

    def __array_shape__(self) -> "VectorProtocol[int]":
        return EmptyVector()

    def __array_index__(self) -> "ArrayIndexProtocol[T]":
        return Always(self)


@dataclasses.dataclass
class Scalar(ScalarProtocol[T]):
    content: T

    def __scalar_content__(self) -> T:
        return self.content


@dataclasses.dataclass
class VectorScalar(ScalarProtocol[T]):
    vector: "VectorProtocol[T]"

    def __scalar_content__(self) -> T:
        return self.vector.__vector_index__()(Scalar(0)).__scalar_content__()


class VectorProtocol(ArrayProtocol[T], typing_extensions.Protocol):
    @abc.abstractmethod
    def __vector_length__(self) -> ScalarProtocol[int]:
        ...

    @abc.abstractmethod
    def __vector_index__(self) -> "VectorIndexProtocol[T]":
        ...

    def __array_shape__(self) -> "VectorProtocol[int]":
        return ScalarVector(self.__vector_length__())

    def __array_index__(self) -> ArrayIndexProtocol[T]:
        def first_idx(v: VectorProtocol[T]) -> ScalarProtocol[T]:
            return VectorScalar(v)

        # def vector_to_scalar(v: VectorProtocol[T]) -> ScalarProtocol[T]:
        #     return ScalarVector(v)
        # def
        return Compose(Box(self.__vector_index__()), Box(first_idx))

        # return Compose(, Box(VectorScalar), Box(self.__vector_index__()))


class VectorIndexProtocol(typing_extensions.Protocol[T]):
    @abc.abstractmethod
    def __call__(self, index: "ScalarProtocol[int]") -> "ScalarProtocol[T]":
        ...


# @dataclasses.dataclass
class EmptyVector(VectorProtocol[T]):
    def __vector_length__(self) -> ScalarProtocol[int]:
        return Scalar(0)

    def __vector_index__(self) -> VectorIndexProtocol[T]:
        return Always(EmptyArray())


@dataclasses.dataclass
class Vector(VectorProtocol[T]):
    length: ScalarProtocol[int]
    index: VectorIndexProtocol[T]

    def __vector_length__(self) -> ScalarProtocol[int]:
        return self.length

    def __vector_index__(self) -> VectorIndexProtocol[T]:
        return self.index


@dataclasses.dataclass
class SequenceVector(VectorProtocol[T]):
    seq: typing.Sequence[T]

    def __vector_length__(self) -> ScalarProtocol[int]:
        return Scalar(len(self.seq))

    def __vector_index__(self) -> VectorIndexProtocol[T]:
        return lambda idx: Scalar(self.seq[idx.__scalar__content__()])


@dataclasses.dataclass
class ScalarVector(VectorProtocol[T]):
    scalar: ScalarProtocol[T]

    def __vector_length__(self) -> ScalarProtocol[int]:
        return Scalar(1)

    def __vector_index__(self) -> VectorIndexProtocol[T]:
        return Always(self.scalar)


# @dataclasses.dataclass
# class Array(typing.Generic[T]):
#     shape: ArrayProtocol[int]
#     getitem: Box[typing.Callable[[ArrayProtocol[int]], ArrayProtocol[T]]]

#     def __shape__(self):
#         return self.shape

#     def __getitem__(self, indices: ArrayProtocol[int]) -> ArrayProtocol[T]:
#         return self.getitem.unboxed(indices)


# class ShapeError(ValueError):
#     pass


# def shape(a: ArrayProtocol[typing.Any]) -> ArrayProtocol[int]:
#     return a.__shape__()


# V = typing.TypeVar("V")


# @functools.singledispatch
# def reduce(
#     a: ArrayProtocol[V], initial: V, fn: typing.Callable[[V, V], V]
# ) -> ArrayProtocol[V]:
#     raise NotImplementedError()


# @functools.singledispatch
# def product(a: ArrayProtocol[T]):
#     return reduce(a, 0, operator.mul)


# @functools.singledispatch
# def is_empty(a: ArrayProtocol[typing.Any]) -> bool:
#     return product(shape(a)) == 0


# @dataclasses.dataclass
# class ScalarArray(ArrayProtocol[T]):
#     content: T

#     def __getitem__(self, indices: ArrayProtocol[int]) -> "ScalarArray[T]":
#         if not is_empty(indices):
#             raise ShapeError()
#         return self

#     def __shape__(self):
#         return VectorArray(tuple())


# @dataclasses.dataclass
# class VectorArray(ArrayProtocol[T], typing.Sequence[T]):
#     contents: typing.Sequence[T]

#     def __getitem__(self, indices: ArrayProtocol[int]) -> ArrayProtocol[T]:
#         return self.contents[indices[(0,)]]

#     def __shape__(self):
#         return VectorArray((len(self.contents),))


# VectorArray([1, 2, 3])

# def vector(contents: typing.Iterable[T]) -> ArrayProtocol[T]:
#     return VectorArray(contents)


# d: ArrayProtocol[int] = VectorArray([1, 2, 3])


# @dataclasses.dataclass
# class AbstractArray(UArrayType[T]):
#     shape: UArrayType[int]
#     psi: typing.Callable[[UArrayType[int]], UArrayType[T]]


# shape: UArrayType[int] = VectorArray([1, 2, 3])
