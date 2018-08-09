import argparse
import json
import os
import time

from typing import Callable, Generator, Tuple, Sequence, Union, Iterable


def has_ext(file_path: str, ext: str):
    """
    Returns True if the extension of file_path is ext

    :param file_path: file path to be examined
    :param ext: extension
    :return: boolean value whether file_path has ext or not
    """
    _, e = os.path.splitext(file_path)

    if ext.startswith('.'):
        return ext == e.strip()
    else:
        return ext == e.strip()[1:]


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


def file_tree_ext(root_path: str, ext: Union[str, Iterable[str]]) -> Generator[str, None, None]:
    """
    Returns a generator which yields all file paths which have `ext` extension in the root_path
    :param root_path: root directory path of files
    :param ext: extension string
    :return: a generator of file paths
    """
    if isinstance(ext, str):
        ext = [ext]

    def pred(file_path):
        return any(has_ext(file_path, e) for e in ext)

    return file_tree(root_path, pred=pred)


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


def save_args(conditions, out_path):
    if isinstance(conditions, argparse.Namespace):
        args = vars(conditions)
    else:
        args = conditions
    args_dict = {k: str(v) for k, v in args.items()}

    with open(os.path.join(out_path, 'args'), 'w') as f:
        json.dump(args_dict, f, indent=4)


class Timer:

    def __init__(self, backend_clock=time.process_time):
        self.backend_clock = backend_clock
        self.cumulative_time = 0

    def reset(self):
        self.cumulative_time = 0

    def _start(self):
        self.start_time = self.now()

    def _stop(self):
        self.cumulative_time += self.now() - self.start_time

    def __enter__(self):
        self._start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop()

    def __str__(self):
        return "{}".format(self.cumulative_time)

    def now(self):
        return self.backend_clock()
