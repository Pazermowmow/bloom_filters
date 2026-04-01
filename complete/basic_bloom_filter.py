from complete.bloom_filter_base import BloomFilterBase

import hashlib
from typing import Self

class BasicBloomFilter(BloomFilterBase):
    def __init__(self, size: int):
        # List of hash functions for adding values to the filter.
        self.hash_functions = [hashlib.md5,
                               hashlib.sha1,
                               hashlib.sha384,
                               hashlib.sha256,
                               hashlib.sha512]

        self.set_bits = 0

        super().__init__(size, nhash=len(self.hash_functions))

    def add (self, item) -> None:
        # For each hash function in the table…
        for ix in range(self.nhash):

            # Get a hashed index for the item…
            index = self.filter_index(item, ix)

            # Get the byte and bit indexes…
            byte_index, bit_index = divmod(index, 8)

            # Create a bit mask for the bit index…
            mask = 1 << bit_index

    
            self.bit_vector[byte_index] |= mask

    def query (self, item) -> bool:
        # For each hash function in the table…
        for ix in range(self.nhash):

            # Get a hashed index for the item…
            index = self.filter_index(item, ix)

            # Get the byte and bit indexes…
            byte_index, bit_index = divmod(index, 8)

            # Create a bit mask for the bit index…
            mask = 1 << bit_index

            # If the matching bit in the vector is 0…
            if (self.bit_vector[byte_index] & mask) == 0:
                # Item is not in the filter…
                return False

        # If none of the bits were 0, item MAY be in the filter…
        return True

    def filter_index(self, data:str, which:int) -> int:
        if which >= self.nhash or which < 0:
            raise ValueError(f"`which` must be between 0 and {self.nhash-1}")

        hasher = self.hash_functions[which]()
        hasher.update(data.encode("utf-8"))

        # Get the digest as hex string and convert to int. This is so that we can
        # use the hash output as bit index to set in the bloom filter.
        digest = int(hasher.hexdigest(), 16) # 16 because hexadecimal

        # Modulo to ensure we get a valid bit index to set in the bloom filter.
        return digest % self.size

    def union(self, other: BloomFilterBase) -> Self:
        if self.size != other.size or self.nhash != other.nhash:
            raise ValueError("Cannot union bloom filters of different sizes or number of hashes")

        result = self.__class__(self.size)
        for i in range(self.nbytes):
            result.bit_vector[i] = self.bit_vector[i] | other.bit_vector[i]

        result.set_bits = result.size - result.blanks()

        return result


bf = BasicBloomFilter(64)
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
print(f'test "am" : {bf.query("am")}')
print()