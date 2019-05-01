import copy
import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))
import stringEditAlgs as stredit


@pytest.fixture
def scanpath_strs():
    return [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
        {'raw_str': 'AB', 'identifier': '02', 'similarity': {'01': 50}},
        {'raw_str': 'AB', 'identifier': '02'}
    ]


def test_remove_valid_scanpath_from_list(scanpath_strs):
    stredit.rem_scanpath_strs_by_id(scanpath_strs, [scanpath_strs[0]['identifier']])
    expected = [
        {'raw_str': 'AB', 'identifier': '02', 'similarity': {}},
        {'raw_str': 'AB', 'identifier': '02'}
    ]

    assert scanpath_strs == expected, \
        "Scanpaths array should have been:\n{}\n, but it was:\n{}\n after removing an element." \
        .format(expected, scanpath_strs)


def test_remove_all_scanpaths_from_list(scanpath_strs):
    ids_to_delete = [scanpath['identifier'] for scanpath in scanpath_strs]
    stredit.rem_scanpath_strs_by_id(scanpath_strs, ids_to_delete)

    assert scanpath_strs == [], \
        "Scanpaths array should have been empty, but it was not:\n{}" \
        .format(scanpath_strs)


def test_remove_non_existing_scanpath_from_list(scanpath_strs):
    with pytest.raises(LookupError) as e:
        stredit.rem_scanpath_strs_by_id(scanpath_strs, ['xx'])