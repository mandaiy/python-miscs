import json
import os
import shutil
from contextlib import contextmanager

from logging import getLogger
from typing import Callable, Generator, Tuple, Sequence

import numpy as np


class OutputDirectory:

    def __init__(self, output_directory: str, *, delete_if_exception=False, logger=None):
        self._logger = logger or getLogger(__name__)

        self._output_directory = output_directory
        self._is_reusing = None
        self._delete_if_exception = delete_if_exception

    @property
    def path(self) -> str:
        return self._output_directory

    @property
    def is_reusing(self) -> bool:
        return self._is_reusing

    def get_decorated_path(self, path: str) -> str:
        return os.path.join(self.path, path)

    def __enter__(self):
        self._is_reusing = os.path.exists(self.path)

        if self.is_reusing:
            self._logger.info("Reuse existing directory '{}'".format(self.path))
        else:
            os.makedirs(self.path)

            self._logger.info("Create new directory '{}'".format(self.path))

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type or exception_value or traceback:

            if not self.is_reusing and self._delete_if_exception:
                self._logger.error("Caught exception. Delete output directory '{}'".format(self.path))

                shutil.rmtree(self.path)

            return False

        return True


class Metadata:

    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def dump(self, file_path):
        obj = {}

        for key in self.__dict__.keys():
            obj[key] = getattr(self, key)

        with open(file_path, 'w') as f:
            json.dump(obj, f, indent=2)

    def __str__(self):
        obj = {}

        for key in self.__dict__.keys():
            obj[key] = getattr(self, key)

        return json.dumps(obj, indent=2)


def file_tree(root_path: str, pred: Callable[[str], bool]=lambda f: True) -> Generator[str, None, None]:
    """
    Returns a generator which yields all file paths in the root_path

    :param pred: predicate function; if this function returns false with a file name, the file is ignored
    :param root_path: root directory path of files
    :return: a generator of file paths
    """
    for dir_path, dir_name, files in os.walk(root_path):
        for file_path in (os.path.join(dir_path, file) for file in files if pred(file)):
            yield file_path


def tuple_to_index(t: Tuple[int, int], size) -> int:
    """
    Returns an index of 1d-array for the given tuple

    :param t:
    :param size:
    :return:
    """
    assert 0 <= t[0] < size and 0 <= t[1] < size, "Out of bound"

    return int(t[0] * size + t[1])  # x * size + y


def index_to_tuple(index: int, size: int) -> Tuple[int, int]:
    """
    Returns a tuple to indicate 2d-array for the given index

    :param index:
    :param size:
    :return:
    """
    assert 0 <= index < size * size, "Out of bound"

    return int(index / size), int(index % size)  # x, y


def divide_sequence_into_chunks(seq: Sequence, chunk_size: int) -> Sequence[Sequence]:
    """
    Returns a sequence which has sequences of the elements in the input sequence
    and each sequence's length is equal to chunk_size.
    If the length of input sequence cannot be divided by chunk_size,
    the last element of return value contains less than chunk_size elements

    >>> divide_sequence_into_chunks([0, 1, 2, 3], chunk_size=2)
    [[0, 1], [2, 3]]

    >>> divide_sequence_into_chunks([0, 1, 2, 3, 4], chunk_size=2)
    [[0, 1], [2, 3], [4]]

    :param seq:
    :param chunk_size:
    :return:
    """
    return [seq[x:x + chunk_size] for x in range(0, len(seq), chunk_size)]


def divide_sequence_by_n(seq: Sequence, n: int) -> Sequence[Sequence]:
    """
    Divides a sequence into n sub-sequences and returns a sequence of the resultant sequences.
    When the length of the given sequence cannot be divided by n,
    the number elements of the first ``len(seq) % n`` elements are greater than ``len(seq) // n`` by 1.

    >>> divide_sequence_by_n([0, 1, 2, 3], 2)  # len(seq) % 2 => 0
    [[0, 1], [2, 3]]
    each element has the equal number of elements

    >>> divide_sequence_by_n([0, 1, 2, 3], 3)  # len(seq) % 3 => 1
    [[0, 1], [2], [3]]
    the number of elements first element has is greater than the others by 1

    >>> divide_sequence_by_n([0, 1, 2, 3, 4], 3)  # len(seq) % 3 => 2
    [[0, 1], [2, 3], [4]]
    the numbers of elements first 2 elements have are greater than the other by 1

    :param seq:
    :param n:
    :return:
    """
    indices = divide_indices_by_n(len(seq), n)

    return [seq[index[0]:index[1]] for index in indices]


def divide_indices_by_n(length: int, n: int):
    chunk_size, remainder = length // n, length % n

    indices = []

    head = 0
    for i in range(n):
        start = head

        if remainder > 0:
            end = head + chunk_size + 1
            remainder -= 1
        else:
            end = head + chunk_size

        indices.append((start, end))

        head = end

    return indices


def suppress_array(arr: np.ndarray, threshold, suppressed_value=0) -> np.ndarray:
    """
    Suppress each element of the given array if the value is less than the `threshold`
    The return value is a different object from the given array
    (i.e., the return value has a different id).
    If `suppressed_value` is given,
    the values to be suppressed are replaced with the `suppressed_value` (default: 0).

    :param arr:
    :param threshold:
    :param suppressed_value:
    :return:
    """
    assert arr.size > 0, "Given array is empty"

    copy = arr.copy()
    copy[arr < threshold] = suppressed_value

    return copy


def ordinal_number(n: int):
    """
    Returns a string representation of the ordinal number for `n`

    e.g.,
    >>> ordinal_number(1)
    '1st'
    >>> ordinal_number(4)
    '4th'
    >>> ordinal_number(21)
    '21st'
    """
    # from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
    return'%d%s' % (n, 'tsnrhtdd'[(n // 10 % 10 != 1) * (n % 10 < 4) * (n % 10)::4])


@contextmanager
def multiple_files(file_paths, opener, mode='r'):
    """
    Context manager of multiple files.

    :param file_paths:
    :param opener:
    :param mode:
    :return:
    """
    if not isinstance(file_paths, list):
        file_paths = [file_paths]

    files = [opener(file_path, mode) for file_path in file_paths]

    yield files

    for file in files:
        file.close()
