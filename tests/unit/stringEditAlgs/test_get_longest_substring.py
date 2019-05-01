import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))
import stringEditAlgs as stredit


@pytest.mark.parametrize("str1, str2, expected", [
    ("hello", "hello", "hello"),
    ("hello", "hello|", "hello"),
    ("hello", "|hello", "hello"),
    ("hello", "hell|o", "hell"),
    ("hello", "hel|l|o", "hel"),
    ("hello", "he|l|l|o", "he"),
    ("hello", "h|e|l|l|o", "h"),
    ("hello", "h|e|l|lo", "lo"),
    ("hello", "h|e|llo", "llo"),
    ("hello", "h|ello", "ello"),
])
def test_longest_substring_if_both_strings_are_valid(str1, str2, expected):
    actual = stredit.get_longest_common_substring(str1, str2)

    assert actual == expected, \
        "Longest common susbtring for strings '{}' and '{}' should have been {}, but it was {}" \
        .format(str1, str2, expected, actual)


@pytest.mark.parametrize("str1, str2, expected", [
    ("", "hello", ""),
    ("hello", "", ""),
])
def test_longest_substring_if_one_string_is_empty(str1, str2, expected):
    actual = stredit.get_longest_common_substring(str1, str2)

    assert actual == expected, \
        "Longest common substring for string '{}' and an empty one should have been {}, but it was {}" \
        .format(str1 if str1 else str2, expected, actual)


def test_longest_substring_if_both_strings_are_empty():
    actual = stredit.get_longest_common_substring("", "")

    assert actual == "", \
        "Longest common substring for a pair of empty strings should have been \"\", but it was {}" \
        .format(actual)
