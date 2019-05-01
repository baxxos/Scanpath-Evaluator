import copy
import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))
import stringEditAlgs as stredit


def test_similarity_of_valid_scanpaths_to_the_common_one():
    scanpath_common = 'AB'
    scanpath_strs = [
        {'raw_str': 'ABCD', 'identifier': '01'},
        {'raw_str': 'AB', 'identifier': '02'}
    ]

    actual = stredit.calc_similarity_to_common(scanpath_strs, scanpath_common)
    expected = {'01': 50, '02': 100}

    assert actual == expected, \
        "Similarity of individual scanpaths:\n{}\nto the common scanpath '{}' was:\n{}\nbut it should have been:\n{}" \
        .format(scanpath_strs, scanpath_common, actual, expected)

def test_similarity_of_valid_scanpaths_an_empty_common_one():
    scanpath_common = ''
    scanpath_strs = [
        {'raw_str': 'ABCD', 'identifier': '01'},
        {'raw_str': 'AB', 'identifier': '02'}
    ]

    actual = stredit.calc_similarity_to_common(scanpath_strs, scanpath_common)
    expected = {}

    assert actual == expected, \
        "Similarity of individual scanpaths:\n{}\nto the common scanpath '{}' was:\n{}\nbut it should have been:\n{}" \
        .format(scanpath_strs, scanpath_common, actual, expected)
