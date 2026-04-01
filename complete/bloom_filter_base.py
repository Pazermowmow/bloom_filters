import abc
from typing import Self

class BloomFilterBase(abc.ABC):
    def __init__(self, size: int, nhash: int):
        # Number of bits in the filter.
        self.size = size

        # Number of hashes to use for adding values to the filter.
        self.nhash = nhash

        # Number of bytes required to store size number of elements
        self.nbytes = (size + 7) // 8

        # Initialize a bytearry with all zeros
        self.bit_vector = bytearray(self.nbytes)

    @abc.abstractmethod
    def query(self, item: str) -> bool:
        ...

    @abc.abstractmethod
    def add(self, item: str) -> None:
        ...

    @abc.abstractmethod
    def union(self, other: Self) -> Self:
        ...

    # Returns the number of unused bits in the filter.
    def blanks (self) -> int:
        func = lambda b:sum(0 if b & pow(2,bx) else 1 for bx in range(8))
        return sum(func(b) for b in self.bit_vector)

    def __len__ (self) -> int: return len(self.bit_vector)
    def __getitem__ (self, ix) -> bytes: return self.bit_vector[ix]
    def __iter__ (self): return iter(self.bit_vector)

    def __str__ (self) -> str:
        return self.vector_to_bits()

    def byte_to_bits (self, b) -> str:
        bs = [('1' if b & pow(2,bx) else '0') for bx in range(8)]
        return "".join(reversed(bs))

    def vector_to_bits (self) -> str:
        bs = [self.byte_to_bits(b) for b in reversed(self.bit_vector)]
        return '.'.join(bs)