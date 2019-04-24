import pytest
import sys
sys.path.append("C:\Users\Baxos\PycharmProjects\Scanpath-Evaluator\src")

import stringEditAlgs as stredit


@pytest.mark.parametrize("str1, str2, expected", [
    ("hello", "hello", 5),
    ("hello", "hhelloo", 5),
    ("hello", "ello", 4),
    ("hello", "llo", 3),
    ("hello", "lo", 2),
    ("hello", "o", 1),
])
def test_lcs_if_both_strings_are_valid(str1, str2, expected):
    stredit.get_longest_common_subsequence()


def test_lcs_if_one_string_is_empty():
    pass


def test_lcs_if_both_strings_are_empty():
    pass
