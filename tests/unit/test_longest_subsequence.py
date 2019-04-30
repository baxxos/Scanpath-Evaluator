import pytest
import sys
sys.path.append("C:\Users\Baxos\PycharmProjects\Scanpath-Evaluator\src")

import stringEditAlgs as stredit


@pytest.mark.parametrize("str1, str2, expected", [
    ("hello", "hello", "hello"),
    ("hello", "h|e|l|l|o", "hello"),
    ("hello", "e|l|l|o", "ello"),
    ("hello", "l|l|o", "llo"),
    ("hello", "l|o", "lo"),
    ("hello", "o", "o"),
])
def test_longest_subsequence_if_both_strings_are_valid(str1, str2, expected):
    actual = stredit.get_longest_common_subsequence(str1, str2)

    assert actual == expected, \
        "Longest common subsequence for string '{}' and '{}' should have been {}, but it was {}" \
        .format(str1, str2, expected, actual)


def test_longest_subsequence_if_one_string_is_empty():
    pass


def test_longest_subsequence_if_both_strings_are_empty():
    pass
