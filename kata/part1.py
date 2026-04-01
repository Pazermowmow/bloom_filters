import abc

class BloomFilterBase(abc.ABC):
    def __init__(self, size: int, nhash: int):
        # TODO: Initialise the bloom filter.
        # We will need to store:
        # - The size (the user defined number of elements the filter can accomodate).
        # - The number of bytes required to accomodate the size.
        # - The number of hashes to use when adding and querying the bloom filter.
        # Additionally, we need to initialise the bit vector (a bytearray).

        self.size = ...
        self.nhash = ...
        self.nbytes = ...
        self.bit_vector = ...

    def blanks (self) -> int:
        func = lambda b:sum(0 if b & pow(2,bx) else 1 for bx in range(8))
        return sum(func(b) for b in self.bit_vector)

    def byte_to_bits (self, b) -> str:
        bs = [('1' if b & pow(2,bx) else '0') for bx in range(8)]
        return "".join(reversed(bs))

    def vector_to_bits (self) -> str:
        bs = [self.byte_to_bits(b) for b in reversed(self.bit_vector)]
        return '.'.join(bs)

    def __len__ (self) -> int: return len(self.bit_vector)
    def __getitem__ (self, ix) -> bytes: return self.bit_vector[ix]
    def __iter__ (self): return iter(self.bit_vector)
    def __str__ (self) -> str:
        return self.vector_to_bits()

    # TODO - Define the abstract methods `query` and `add` to be used by our concrete implementations.
    # @abc.abstractmethod
    # def add(self, ...): ...

    # @abc.abstractmethod
    # def query(self, ...): ...

    # @abc.abstractmethod
    # def union(self, ...): ...