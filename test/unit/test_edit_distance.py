import pytest
import sys
sys.path.append("C:\Users\Baxos\PycharmProjects\Scanpath-Evaluator\src")

import stringEditAlgs as stredit


@pytest.mark.parametrize("str1, str2, expected", [
    ("hello", "hello", 0),
    ("hello", "helo", 1),
    ("hello", "olleh", 4),
    ("hello", "aaaaa", 5),
])
def test_edit_distance_calc_if_both_strings_are_valid(str1, str2, expected):
    actual = stredit.get_edit_distance(str1, str2)

    assert actual == expected, \
        "Edit distance for strings '{}' and '{}' should have been {}, but it was {}" \
        .format(str1, str2, expected, actual)


@pytest.mark.parametrize("str1, str2, expected", [
    ("hello", "", 5),
    ("", "hello", 5),
])
def test_edit_distance_calc_if_one_string_is_empty(str1, str2, expected):
    actual = stredit.get_edit_distance(str1, str2)

    assert actual == expected, \
        "Edit distance for string '{}' and an empty one should have been {}, but it was {}" \
        .format(str1 if str1 else str2, expected, actual)


def test_edit_distance_calc_if_both_strings_are_empty():
    assert stredit.get_edit_distance("", "") == 0, \
        "Edit distance for a pair of empty strings should have been 0"
