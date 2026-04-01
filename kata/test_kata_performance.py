# ---------------------------------------------------------------------------
# Performance comparison tests
# Run with `pytest test_kata_performance.py -rA` for detailed output on passing tests.
# ---------------------------------------------------------------------------

# from kata_part2 import BasicBloomFilter
# from kata_part3 import OptimisedBloomFilter
from complete.basic_bloom_filter import BasicBloomFilter
from complete.optimised_bloom_filter import OptimisedBloomFilter

import time
from pytest import mark


class TestPerformanceComparison:
    """Compare add/query speed between BasicBloomFilter and OptimisedBloomFilter."""

    FILTER_SIZE = 8192
    NUM_ITEMS = 5000

    def _words(self):
        return [f"word_{i}" for i in range(self.NUM_ITEMS)]

    @mark.perf
    def test_add_optimised_faster_than_basic(self):
        words = self._words()

        bf_basic = BasicBloomFilter(self.FILTER_SIZE)
        start = time.perf_counter()
        for w in words:
            bf_basic.add(w)
        basic_time = time.perf_counter() - start

        bf_opt = OptimisedBloomFilter(self.FILTER_SIZE)
        start = time.perf_counter()
        for w in words:
            bf_opt.add(w)
        opt_time = time.perf_counter() - start

        speedup = basic_time / opt_time
        print(f"\n  Add {self.NUM_ITEMS} items — basic: {basic_time:.4f}s, optimised: {opt_time:.4f}s ({speedup:.1f}x faster)")
        assert opt_time < basic_time, (
            f"Expected optimised ({opt_time:.4f}s) to be faster than basic ({basic_time:.4f}s)"
        )

    @mark.perf
    def test_query_optimised_faster_than_basic(self):
        words = self._words()

        bf_basic = BasicBloomFilter(self.FILTER_SIZE)
        bf_opt = OptimisedBloomFilter(self.FILTER_SIZE)
        for w in words:
            bf_basic.add(w)
            bf_opt.add(w)

        start = time.perf_counter()
        for w in words:
            bf_basic.query(w)
        basic_time = time.perf_counter() - start

        start = time.perf_counter()
        for w in words:
            bf_opt.query(w)
        opt_time = time.perf_counter() - start

        speedup = basic_time / opt_time
        print(f"\n  Query {self.NUM_ITEMS} items — basic: {basic_time:.4f}s, optimised: {opt_time:.4f}s ({speedup:.1f}x faster)")
        assert opt_time < basic_time, (
            f"Expected optimised ({opt_time:.4f}s) to be faster than basic ({basic_time:.4f}s)"
        )