import unittest

from python_utils import tuple_to_index, index_to_tuple, divide_sequence_into_chunks, divide_sequence_by_n


class TestUtils(unittest.TestCase):

    def test_tuple_to_index_when_tuple_is_out_of_bound_then_raises_exception(self):
        size = 9

        self.assertRaises(AssertionError, tuple_to_index, (0, -1), size)
        self.assertRaises(AssertionError, tuple_to_index, (-1, 0), size)
        self.assertRaises(AssertionError, tuple_to_index, (9, 0), size)
        self.assertRaises(AssertionError, tuple_to_index, (0, 9), size)

    def test_tuple_to_index_is_compatible_with_index_to_tuple(self):
        size = 9
        expected = (3, 3)

        self.assertEqual(expected, index_to_tuple(tuple_to_index(expected, size), size))

    def test_index_to_tuple_when_tuple_is_out_of_bound_then_raises_exception(self):
        size = 9

        self.assertRaises(AssertionError, index_to_tuple, -1, size)
        self.assertRaises(AssertionError, index_to_tuple, 81, size)

    def test_index_to_tuple_is_compatible_with_tuple_to_index(self):
        size = 9
        expected = 30

        self.assertEqual(expected, tuple_to_index(index_to_tuple(expected, size), size))

    def test_divide_sequence_by_n_when_input_length_is_dividable_by_n(self):
        seq = list(range(10))
        n = 2

        self.assertEqual(divide_sequence_by_n(seq, n), [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])

    def test_divide_sequence_by_n_when_input_length_is_indivisible_by_n(self):
        seq = list(range(10))
        n = 3

        self.assertEqual(divide_sequence_by_n(seq, n), [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def test_divide_sequence_into_chunks_when_input_length_is_divisible_by_chunk_size_then_returns_exactly_chunk_size_elements(self):
        seq = [0, 1, 2, 3]
        chunk_size = 2

        expected = [[0, 1], [2, 3]]
        actual = divide_sequence_into_chunks(seq, chunk_size)

        self.assertEqual(expected, actual)

    def test_divide_sequence_into_chunks_when_input_length_is_indivisible_by_chunk_size_then_returns_remainder_elements(self):
        seq = [0, 1, 2, 3, 4]
        chunk_size = 2

        expected = [[0, 1], [2, 3], [4]]
        actual = divide_sequence_into_chunks(seq, chunk_size)

        self.assertEqual(expected, actual)
