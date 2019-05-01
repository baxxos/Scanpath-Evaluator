import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))
import stringEditAlgs as stredit

@pytest.mark.parametrize("scanpath_strs, expected", [
    (
        [
            {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
            {'raw_str': 'AB', 'identifier': '02', 'similarity': {'01': 50}}
        ], 
        [
            {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
            {'raw_str': 'AB', 'identifier': '02', 'similarity': {'01': 50}},
            50
        ]
    ),
    (
        [
            {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 75, '03': 25}},
            {'raw_str': 'ABC', 'identifier': '02', 'similarity': {'01': 75, '03': 33}},
            {'raw_str': 'A', 'identifier': '03', 'similarity': {'01': 25, '02': 33}}
        ],
        [
            {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 75, '03': 25}},
            {'raw_str': 'ABC', 'identifier': '02', 'similarity': {'01': 75, '03': 33}},
            75
        ]
    ),
])
def test_of_most_similar_pair_if_all_scanpaths_are_valid(scanpath_strs, expected):

    actual = stredit.get_most_similar_pair(scanpath_strs)

    assert actual == expected, \
        "Most similar pair from following scanpaths:\n{}\nshould have been:\n{}\nbut it was:\n{}\n" \
        .format(scanpath_strs, expected, actual)

def test_of_most_similar_pair_if_all_scanpaths_are_empty():
    scanpath_strs = [
        {'raw_str': '', 'identifier': '01', 'similarity': {'02': 100}},
        {'raw_str': '', 'identifier': '02', 'similarity': {'01': 100}}
    ]

    actual = stredit.get_most_similar_pair(scanpath_strs)
    expected = [
        {'raw_str': '', 'identifier': '01', 'similarity': {'02': 100}},
        {'raw_str': '', 'identifier': '02', 'similarity': {'01': 100}},
        100
    ]

    assert actual == expected, \
        "Most similar pair from following scanpaths:\n{}\nshould have been:\n{}\nbut it was:\n{}\n" \
        .format(scanpath_strs, expected, actual)

