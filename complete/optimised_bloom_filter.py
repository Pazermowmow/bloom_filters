from complete.bloom_filter_base import BloomFilterBase

import hashlib
from typing import Self

class OptimisedBloomFilter(BloomFilterBase):
    def __init__ (self, size: int):
        super().__init__(size, nhash=5)

        self.hash_func = hashlib.blake2b
        self.key1, self.key2 = b'key1', b'key2'

    def filter_indexes(self, data:str) -> list[int]:
        hash1 = self.hash_func(
            data.encode("utf-8"),
            digest_size=8,
            key=self.key1,
        ).digest()

        hash2 = self.hash_func(
            data.encode("utf-8"),
            digest_size=8,
            key=self.key2,
        ).digest()

        h1 = int.from_bytes(hash1, byteorder="big")
        h2 = int.from_bytes(hash2, byteorder="big")

        return [(h1 + i * h2) % self.size for i in range(self.nhash)]

    def query (self, item) -> bool:
        for index in self.filter_indexes(item):
            byte_index, bit_index = divmod(index, 8)
            mask = 1 << bit_index

            # If the matching bit in the vector is 0…
            if (self.bit_vector[byte_index] & mask) == 0:
                # Item is not in the filter…
                return False

        # If none of the bits were 0, item MAY be in the filter…
        return True

    def add (self, item) -> None:
        for index in self.filter_indexes(item):
            # Get the byte and bit indexes…
            byte_index, bit_index = divmod(index, 8)

            # Create a bit mask for the bit index…
            mask = 1 << bit_index

            # Set the index bit in the vector…
            self.bit_vector[byte_index] |= mask

    def union(self, other: BloomFilterBase) -> Self:
        if self.size != other.size or self.nhash != other.nhash:
            raise ValueError("Cannot union bloom filters of different sizes or number of hashes")

        result = self.__class__(self.size)
        for i in range(self.nbytes):
            result.bit_vector[i] = self.bit_vector[i] | other.bit_vector[i]

        return result
            

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


bf = OptimisedBloomFilter(64)
for w in ['who', 'what', 'why', 'where', 'when']:
    bf.add(w)

print(f'{bf=!s}')
print(f'> blanks={bf.blanks()}')
print()
print(f'test "" : {bf.query("")}')
print(f'test "when" : {bf.query("when")}')
print(f'test "went" : {bf.query("went")}')
print(f'test "why" : {bf.query("why")}')
print(f'test "why not": {bf.query("why not")}')
print(f'test "where" : {bf.query("where")}')
print(f'test "who" : {bf.query("who")}')
print(f'test "wh" : {bf.query("wh")}')
print(f'test "hyperleptoprosopic" : {bf.query("hyperleptoprosopic")}')