import os
import pytest
import sys

import src.stringEditAlgs as stredit


@pytest.mark.parametrize("scanpath1, scanpath2, expected", [
    ("ABCD", "A", 25),
    ("ABCD", "AB", 50),
    ("ABCD", "ABC", 75),
    ("ABCD", "ABCD", 100),
])
def test_similarity_if_both_scanpaths_are_valid(scanpath1, scanpath2, expected):
    actual = stredit.calc_similarity(scanpath1, scanpath2)

    assert actual == expected, \
        "Percentual similarity of scanpaths '{}' and '{}' should have been {}, but it was {}" \
        .format(scanpath1, scanpath2, expected, actual)


@pytest.mark.parametrize("scanpath1, scanpath2, expected", [
    ("ABCD", "", 0),
    ("", "ABCD", 0),
])
def test_similarity_if_one_scanpath_is_empty(scanpath1, scanpath2, expected):
    actual = stredit.calc_similarity(scanpath1, scanpath2)

    assert actual == expected, \
        "Percentual similarity of scanpaths '{}' and an empty one should have been {}, but it was {}" \
        .format(scanpath1 if scanpath1 else scanpath2, expected, actual)


def test_similarity_if_both_scanpaths_are_empty():
    expected = 100
    actual = stredit.calc_similarity("", "")

    assert actual == 0, \
        "Percentual similarity of a pair of empty scanpaths should have been {}, but it was {}" \
        .format(expected, actual)