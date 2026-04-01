# Bloom Filter Kata

Complete the implementations to create a working bloom filter.

1. Part 1 - bloom filter base. This is the abstract class providing the interface for the concrete implementations.
2. Part 2 - basic implementation. Use the 5 predefined hashes to produce the bits to set in the bloom filter.
3. Part 3 - optimised implementation. Use the "2 hash optimisation" described in Howard Bloom's paper to create a far more efficient and scalable implementation of a bloom filter.
4. Performance testing - run the tests in `kata/test_kata_performance.py` and mess with some of the parameters to see how much more efficient the optimised implementation is.
5. Invent a scenario - calculate optimum parameters for a given number of elements to store + test false positive rate when using sub-optimal parameters.
6. Unioning of blooms - two blooms can be combined by simply OR'ing their respective bitsets. How would you calculate when combining two blooms would produce an over saturated bloom?

Solutions for tasks 1-3 are provided in `complete/`. (The remaining points are more open-ended investigation).

