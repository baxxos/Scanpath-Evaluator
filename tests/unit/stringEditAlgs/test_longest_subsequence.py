import stringEditAlgs as stredit
import os
import pytest
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))


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
        "Longest common subsequence for strings '{}' and '{}' should have been {}, but it was {}" \
        .format(str1, str2, expected, actual)


@pytest.mark.parametrize("str1, str2, expected", [
    ("hello", "", ""),
    ("", "hello", ""),
])
def test_longest_subsequence_if_one_string_is_empty(str1, str2, expected):
    actual = stredit.get_longest_common_subsequence(str1, str2)

    assert actual == expected, \
        "Longest common subsequence for string '{}' and an empty one should have been {}, but it was {}" \
        .format(str1 if str1 else str2, expected, actual)


def test_longest_subsequence_if_both_strings_are_empty():
    actual = stredit.get_longest_common_subsequence("", "")

    assert actual == "", \
        "Longest common subsequence for a pair of empty strings should have been \"\", but it was {}" \
        .format(actual)
