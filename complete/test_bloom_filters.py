"""
Unit tests for the Bloom Filter kata.

Run with:  pytest test_bloom_filters.py -v
"""

import pytest
import hashlib

from complete.basic_bloom_filter import BasicBloomFilter
from complete.optimised_bloom_filter import OptimisedBloomFilter

# ---------------------------------------------------------------------------
# BloomFilterBase tests
# ---------------------------------------------------------------------------

class TestBloomFilterBaseInit:
    """Checks for BloomFilterBase.__init__"""

    def test_nbytes_exact_multiple(self):
        """When size is an exact multiple of 8, nbytes == size // 8."""
        bf = BasicBloomFilter(size=64)
        assert bf.nbytes == 8

    def test_bit_vector_is_bytearray(self):
        bf = BasicBloomFilter(size=64)
        assert isinstance(bf.bit_vector, bytearray)

    def test_bit_vector_length_matches_nbytes(self):
        bf = BasicBloomFilter(size=64)
        assert len(bf.bit_vector) == bf.nbytes

    def test_bit_vector_initialised_to_zeros(self):
        bf = BasicBloomFilter(size=64)
        assert all(b == 0 for b in bf.bit_vector)


class TestBloomFilterBaseBlanks:
    """Checks for BloomFilterBase.blanks"""

    def _make_bf(self, size: int):
        return BasicBloomFilter(size=size)

    def test_blanks_all_zeros(self):
        """A fresh filter should have size bits available (rounded up to full bytes)."""
        bf = self._make_bf(64)
        assert bf.blanks() == 64

    def test_blanks_after_setting_a_bit(self):
        bf = self._make_bf(64)
        bf.bit_vector[0] = 0b00000001  # set 1 bit
        assert bf.blanks() == 63

    def test_blanks_after_filling_a_byte(self):
        bf = self._make_bf(64)
        bf.bit_vector[0] = 0xFF  # all 8 bits set
        assert bf.blanks() == 56


class TestBloomFilterBaseDunders:
    """Checks for __len__, __getitem__, __iter__, __str__"""

    def _make_bf(self, size):
        return BasicBloomFilter(size=size)

    def test_len_returns_bytearray_length(self):
        bf = self._make_bf(64)
        assert len(bf) == 8

    def test_getitem_returns_byte_value(self):
        bf = self._make_bf(64)
        bf.bit_vector[0] = 42
        assert bf[0] == 42

    def test_iter_yields_all_bytes(self):
        bf = self._make_bf(16)
        bf.bit_vector[0] = 1
        bf.bit_vector[1] = 2
        assert list(bf) == [1, 2]

    def test_str_returns_string(self):
        bf = self._make_bf(16)
        result = str(bf)
        assert isinstance(result, str)
        assert len(result) > 0


class TestBloomFilterBaseBitConversions:
    """Checks for byte_to_bits and vector_to_bits"""

    def _make_bf(self, size):
        return BasicBloomFilter(size=size)

    def test_byte_to_bits_zero(self):
        bf = self._make_bf(8)
        assert bf.byte_to_bits(0) == "00000000"

    def test_byte_to_bits_one(self):
        bf = self._make_bf(8)
        assert bf.byte_to_bits(1) == "00000001"

    def test_byte_to_bits_255(self):
        bf = self._make_bf(8)
        assert bf.byte_to_bits(255) == "11111111"

    def test_byte_to_bits_170(self):
        """0b10101010 == 170"""
        bf = self._make_bf(8)
        assert bf.byte_to_bits(0b10101010) == "10101010"

    def test_vector_to_bits_all_zeros(self):
        bf = self._make_bf(16)
        assert bf.vector_to_bits() == "00000000.00000000"

    def test_vector_to_bits_some_bits_set(self):
        bf = self._make_bf(16)
        bf.bit_vector[0] = 0b00000001
        # Reversed byte order in output: byte[1] first, then byte[0]
        assert bf.vector_to_bits() == "00000000.00000001"

    def test_vector_to_bits_dot_separated(self):
        bf = self._make_bf(24)
        parts = bf.vector_to_bits().split(".")
        assert len(parts) == 3


# ---------------------------------------------------------------------------
# BasicBloomFilter tests
# ---------------------------------------------------------------------------

class TestBasicBloomFilterInit:
    """Checks for BasicBloomFilter.__init__"""

    def test_has_five_hash_functions(self):
        bf = BasicBloomFilter(64)
        assert len(bf.hash_functions) == 5

    def test_nhash_matches_hash_functions_count(self):
        bf = BasicBloomFilter(64)
        assert bf.nhash == len(bf.hash_functions)

    def test_size_is_set(self):
        bf = BasicBloomFilter(128)
        assert bf.size == 128

    def test_hash_functions_are_callable(self):
        bf = BasicBloomFilter(64)
        for hf in bf.hash_functions:
            hasher = hf()
            hasher.update(b"test")
            # Should produce a hex digest without error
            assert len(hasher.hexdigest()) > 0


class TestBasicBloomFilterFilterIndex:
    """Checks for BasicBloomFilter.filter_index"""

    def test_returns_int(self):
        bf = BasicBloomFilter(64)
        result = bf.filter_index("hello", 0)
        assert isinstance(result, int)

    def test_result_within_range(self):
        bf = BasicBloomFilter(64)
        for which in range(bf.nhash):
            idx = bf.filter_index("test", which)
            assert 0 <= idx < 64

    def test_deterministic(self):
        """Same input + same hash index → same output."""
        bf = BasicBloomFilter(64)
        a = bf.filter_index("hello", 0)
        b = bf.filter_index("hello", 0)
        assert a == b

    def test_different_hash_functions_may_differ(self):
        """Different hash indexes should (usually) produce different indices."""
        bf = BasicBloomFilter(1024)
        indices = {bf.filter_index("hello", i) for i in range(bf.nhash)}
        # With a large filter, it's very unlikely all 5 hashes collide.
        assert len(indices) > 1

    def test_raises_on_invalid_which_too_high(self):
        bf = BasicBloomFilter(64)
        with pytest.raises(ValueError):
            bf.filter_index("hello", bf.nhash)

    def test_raises_on_invalid_which_negative(self):
        bf = BasicBloomFilter(64)
        with pytest.raises(ValueError):
            bf.filter_index("hello", -1)


class TestBasicBloomFilterAdd:
    """Checks for BasicBloomFilter.add"""

    def test_add_changes_bit_vector(self):
        bf = BasicBloomFilter(64)
        before = bf.blanks()
        bf.add("hello")
        after = bf.blanks()
        assert after < before, "Adding an item should set at least one bit"

    def test_add_is_idempotent(self):
        """Adding the same item twice should not change the vector further."""
        bf = BasicBloomFilter(64)
        bf.add("hello")
        snapshot = bytearray(bf.bit_vector)
        bf.add("hello")
        assert bf.bit_vector == snapshot

    def test_add_multiple_items(self):
        bf = BasicBloomFilter(64)
        bf.add("alpha")
        blanks_after_one = bf.blanks()
        bf.add("beta")
        blanks_after_two = bf.blanks()
        assert blanks_after_two <= blanks_after_one


class TestBasicBloomFilterQuery:
    """Checks for BasicBloomFilter.query"""

    def test_query_empty_filter_returns_false(self):
        bf = BasicBloomFilter(64)
        assert bf.query("hello") is False

    def test_query_after_add_returns_true(self):
        bf = BasicBloomFilter(64)
        bf.add("hello")
        assert bf.query("hello") is True

    def test_query_unadded_item_returns_false(self):
        bf = BasicBloomFilter(1024)  # large to reduce false positives
        bf.add("hello")
        assert bf.query("goodbye") is False

    def test_query_returns_bool(self):
        bf = BasicBloomFilter(64)
        assert isinstance(bf.query("anything"), bool)

    def test_query_multiple_added_items(self):
        bf = BasicBloomFilter(1024)
        words = ["who", "what", "why", "where", "when"]
        for w in words:
            bf.add(w)
        for w in words:
            assert bf.query(w) is True, f"Expected '{w}' to be found"

    def test_query_items_not_added(self):
        bf = BasicBloomFilter(1024)
        words = ["who", "what", "why", "where", "when"]
        for w in words:
            bf.add(w)
        # These should (almost certainly) not be found with a 1024-bit filter
        for w in ["went", "wh", "am", "hyperleptoprosopic"]:
            assert bf.query(w) is False, f"Did not expect '{w}' to be found"


class TestBasicBloomFilterBlanks:
    """Checks for BasicBloomFilter.blanks"""

    def test_blanks_starts_at_size(self):
        bf = BasicBloomFilter(64)
        assert bf.blanks() == 64

    def test_blanks_decreases_after_add(self):
        bf = BasicBloomFilter(64)
        bf.add("hello")
        assert bf.blanks() < 64


class TestBasicBloomFilterStringRepresentation:
    """Checks for __str__, byte_to_bits, vector_to_bits on BasicBloomFilter"""

    def test_str_of_empty_filter(self):
        bf = BasicBloomFilter(16)
        assert str(bf) == "00000000.00000000"

    def test_str_changes_after_add(self):
        bf = BasicBloomFilter(16)
        before = str(bf)
        bf.add("x")
        after = str(bf)
        assert before != after


# ---------------------------------------------------------------------------
# OptimisedBloomFilter tests
# ---------------------------------------------------------------------------

class TestOptimisedBloomFilterInit:
    """Checks for OptimisedBloomFilter.__init__"""

    def test_nhash_is_five(self):
        bf = OptimisedBloomFilter(64)
        assert bf.nhash == 5

    def test_size_is_stored(self):
        bf = OptimisedBloomFilter(128)
        assert bf.size == 128

    def test_hash_func_is_blake2b(self):
        bf = OptimisedBloomFilter(64)
        assert bf.hash_func is hashlib.blake2b

    def test_keys_are_set(self):
        bf = OptimisedBloomFilter(64)
        assert bf.key1 == b'key1'
        assert bf.key2 == b'key2'


class TestOptimisedBloomFilterFilterIndexes:
    """Checks for OptimisedBloomFilter.filter_indexes"""

    def test_returns_list(self):
        bf = OptimisedBloomFilter(64)
        result = bf.filter_indexes("hello")
        assert isinstance(result, list)

    def test_returns_nhash_indexes(self):
        bf = OptimisedBloomFilter(64)
        result = bf.filter_indexes("hello")
        assert len(result) == bf.nhash

    def test_all_indexes_in_range(self):
        bf = OptimisedBloomFilter(64)
        for idx in bf.filter_indexes("hello"):
            assert 0 <= idx < 64

    def test_deterministic(self):
        bf = OptimisedBloomFilter(64)
        a = bf.filter_indexes("hello")
        b = bf.filter_indexes("hello")
        assert a == b

    def test_different_inputs_give_different_indexes(self):
        bf = OptimisedBloomFilter(1024)
        a = bf.filter_indexes("hello")
        b = bf.filter_indexes("world")
        assert a != b

    def test_indexes_are_ints(self):
        bf = OptimisedBloomFilter(64)
        for idx in bf.filter_indexes("test"):
            assert isinstance(idx, int)


class TestOptimisedBloomFilterAdd:
    """Checks for OptimisedBloomFilter.add"""

    def test_add_changes_bit_vector(self):
        bf = OptimisedBloomFilter(64)
        before = bf.blanks()
        bf.add("hello")
        after = bf.blanks()
        assert after < before

    def test_add_is_idempotent(self):
        bf = OptimisedBloomFilter(64)
        bf.add("hello")
        snapshot = bytearray(bf.bit_vector)
        bf.add("hello")
        assert bf.bit_vector == snapshot

    def test_add_multiple_items(self):
        bf = OptimisedBloomFilter(64)
        bf.add("alpha")
        blanks_after_one = bf.blanks()
        bf.add("beta")
        blanks_after_two = bf.blanks()
        assert blanks_after_two <= blanks_after_one


class TestOptimisedBloomFilterQuery:
    """Checks for OptimisedBloomFilter.query"""

    def test_query_empty_filter_returns_false(self):
        bf = OptimisedBloomFilter(64)
        assert bf.query("hello") is False

    def test_query_after_add_returns_true(self):
        bf = OptimisedBloomFilter(64)
        bf.add("hello")
        assert bf.query("hello") is True

    def test_query_unadded_item_returns_false(self):
        bf = OptimisedBloomFilter(1024)
        bf.add("hello")
        assert bf.query("goodbye") is False

    def test_query_returns_bool(self):
        bf = OptimisedBloomFilter(64)
        assert isinstance(bf.query("anything"), bool)

    def test_query_multiple_added_items(self):
        bf = OptimisedBloomFilter(1024)
        words = ["who", "what", "why", "where", "when"]
        for w in words:
            bf.add(w)
        for w in words:
            assert bf.query(w) is True, f"Expected '{w}' to be found"

    def test_query_items_not_added(self):
        bf = OptimisedBloomFilter(1024)
        words = ["who", "what", "why", "where", "when"]
        for w in words:
            bf.add(w)
        for w in ["went", "wh", "am", "hyperleptoprosopic"]:
            assert bf.query(w) is False, f"Did not expect '{w}' to be found"


class TestOptimisedBloomFilterBlanks:
    """Checks for OptimisedBloomFilter.blanks"""

    def test_blanks_starts_at_size(self):
        bf = OptimisedBloomFilter(64)
        assert bf.blanks() == 64

    def test_blanks_decreases_after_add(self):
        bf = OptimisedBloomFilter(64)
        bf.add("hello")
        assert bf.blanks() < 64


class TestOptimisedBloomFilterStringRepresentation:
    """Checks for __str__, byte_to_bits, vector_to_bits on OptimisedBloomFilter"""

    def test_str_of_empty_filter(self):
        bf = OptimisedBloomFilter(16)
        assert str(bf) == "00000000.00000000"

    def test_str_changes_after_add(self):
        bf = OptimisedBloomFilter(16)
        before = str(bf)
        bf.add("x")
        after = str(bf)
        assert before != after


# ---------------------------------------------------------------------------
# Test union of bloom filters
# ---------------------------------------------------------------------------

class TestBloomFilterUnion:
    """Checks for union method on both BasicBloomFilter and OptimisedBloomFilter"""

    def test_union_of_empty_filters(self):
        bf1 = BasicBloomFilter(64)
        bf2 = BasicBloomFilter(64)
        result = bf1.union(bf2)
        assert isinstance(result, BasicBloomFilter)
        assert result.blanks() == 64

    def test_union_of_different_sizes_raises(self):
        bf1 = BasicBloomFilter(64)
        bf2 = BasicBloomFilter(128)
        with pytest.raises(ValueError):
            bf1.union(bf2)

    def test_union_of_different_nhash_raises(self):
        # Create a custom bloom filter with different nhash for testing
        class CustomBloomFilter(BasicBloomFilter):
            def __init__(self, size):
                super().__init__(size)
                self.nhash = 3  # different from the default 5

        bf1 = BasicBloomFilter(64)
        bf2 = CustomBloomFilter(64)
        with pytest.raises(ValueError):
            bf1.union(bf2)

    def test_union_combines_bits(self):
        bf1 = BasicBloomFilter(64)
        bf2 = BasicBloomFilter(64)
        bf3 = BasicBloomFilter(64)

        # Add different items to each filter
        bf1.add("hello")
        bf2.add("world")

        bf3.add("hello")
        bf3.add("world")

        assert bf1.set_bits != bf3.set_bits
        assert bf2.set_bits != bf3.set_bits
        result = bf1.union(bf2)

        # The union should have bits set for both "hello" and "world"
        assert result.query("hello") is True
        assert result.query("world") is True
        assert result.set_bits == bf3.set_bits
