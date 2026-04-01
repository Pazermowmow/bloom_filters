from kata.part1 import BloomFilterBase

import hashlib
from typing import Self

class BasicBloomFilter(BloomFilterBase):
    def __init__(self, size: int):
        # TODO: Initialise the BasicBloomFilter.
        # Our `super()` class BloomFilterBase already has an __init__ method that initialises the size, number of hashes, and bit vector.
        # We just need to call `super().__init__()` with the appropriate arguments.
        
        # The list of hash functions to use for adding and retrieving values.
        self.hash_functions = [
            hashlib.md5,
            hashlib.sha1,
            hashlib.sha384,
            hashlib.sha256,
            hashlib.sha512,
        ]
        ...

    def add(self, item) -> None:
        # TODO:
        # We will use each of the class' hash functions to determine a bit to set.
        # For each hash function:
        # 1. Hash the item (encoded as utf-8).
        # 2. Convert the hash hexdigest to an integer.
        # 3. Modulo the integer by self.size to get a bit index.
        # 4. Find the byte within the bytearray and the bit within that byte to set. (Hint: use divmod)
        # 5. Create a bitmask with (1 << bit_index) and set the corresponding bit in self.bit_vector using a bitwise OR.
        raise NotImplementedError

    def query(self, item) -> bool:
        # TODO:
        # Same process as `add()`, but instead of setting bits, we check if the bits are already set.
        # If any of the bits are not set, we can return False immediately.
        # If all bits are set, we return True (indicating the item may be in the filter with some probability).
        raise NotImplementedError

    def union(self, other: BloomFilterBase) -> Self:
        # TODO:
        # Combine the bit vectors of two bloom filters using a bitwise OR operation to create a single new bloom filter.
        raise NotImplementedError
        