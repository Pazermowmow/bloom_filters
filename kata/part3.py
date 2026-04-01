from complete.bloom_filter_base import BloomFilterBase

import hashlib
from typing import Self


class OptimisedBloomFilter(BloomFilterBase):
    def __init__(self, size: int):
        # TODO:
        # There is an optimisation we can make to reduce the number of hash computations from k to 2, while still generating k indexes.
        # We can do this using two different seeded hashes and the formula:
        # index = (h1 + i * h2) % self.size to determine the bit positions to set.

        ...

    def filter_indexes(self, data: str) -> list[int]:
        # TODO:
        # For a given input data, compute the list of indexes to set/check.
        raise NotImplementedError

    def add(self, item) -> None:
        # TODO:
        # As before, but now we are using the 2 hash optimisation instead of 5 separate hash functions.
        raise NotImplementedError

    def query(self, item) -> bool:
        # TODO:
        # As before, but now we are using the 2 hash optimisation instead of 5 separate hash functions.
        raise NotImplementedError

    def union(self, other: BloomFilterBase) -> Self:
        # TODO:
        # As before
        raise NotImplementedError

