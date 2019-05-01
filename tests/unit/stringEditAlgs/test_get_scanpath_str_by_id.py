import os
import pytest
import sys

import src.stringEditAlgs as stredit


@pytest.fixture
def scanpath_strs():
    return [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
        {'raw_str': 'AB', 'identifier': '02', 'similarity': {'01': 50}}
    ]


def test_get_scanpath_by_id_if_present_in_the_list(scanpath_strs):
    expected = scanpath_strs[0]
    actual = stredit.get_scanpath_str_by_id(scanpath_strs, '01')

    assert actual == expected, \
        "Retrieved scanpath should have been:\n{}\nbut it was:\n{}" \
        .format(expected, actual)

    expected = scanpath_strs[1]
    actual = stredit.get_scanpath_str_by_id(scanpath_strs, '02')

    assert actual == expected, \
        "Retrieved scanpath should have been:\n{}\nbut it was:\n{}" \
        .format(expected, actual)


def test_get_scanpath_by_id_if_not_present_in_the_list(scanpath_strs):
    with pytest.raises(LookupError) as e:
        stredit.get_scanpath_str_by_id(scanpath_strs, 'xx')