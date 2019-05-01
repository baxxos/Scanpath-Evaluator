import os
import pytest
import sys

import src.stringEditAlgs as stredit


def test_remove_mutual_scanpath_similarities():
    scanpath_strs = [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
        {'raw_str': 'AB', 'identifier': '02', 'similarity': {'01': 50}},
        {'raw_str': 'AB', 'identifier': '02'}
    ]

    expected = [
        {'raw_str': 'ABCD', 'identifier': '01'},
        {'raw_str': 'AB', 'identifier': '02'},
        {'raw_str': 'AB', 'identifier': '02'}
    ]

    stredit.clear_mutual_similarity(scanpath_strs)

    assert scanpath_strs == expected, \
        "Scanpaths array should not have contained mutual similarity values:\n{}" \
        .format(scanpath_strs)
