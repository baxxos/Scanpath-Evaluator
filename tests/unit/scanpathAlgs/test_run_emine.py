import pytest

import src.scanpathAlgs.emine as emine


@pytest.mark.parametrize("raw_sequences, common_scanpath_expected", [
    (
        {
            'P01': [['A', 100], ['B', 100]],
            'P02': [['A', 100], ['B', 100], ['B', 100], ['C', 100]]
        },
        {
            'identifier': 'eMINE',
            'fixations': [['A', 0], ['B', 0]],
            'similarity': {
                'P01': 100,
                'P02': 50
            }
        }
    ),
    (
        {
            'P01': [['A', 100], ['B', 100]],
            'P02': [['A', 100], ['B', 100], ['B', 100], ['C', 100]],
            'P03': [['C', 100], ['A', 100], ['B', 100], ['D', 100]],
        },
        {
            'identifier': 'eMINE',
            'fixations': [['A', 0], ['B', 0]],
            'similarity': {
                'P01': 100,
                'P02': 50,
                'P03': 50,
            }
        }
    )
])
def test_run_emine_and_expect_reasonable_common_scanpath(raw_sequences, common_scanpath_expected):
    common_scanpath_actual = emine.run_emine(raw_sequences)

    assert common_scanpath_actual == common_scanpath_expected, \
        "Common scanpath should have been:\n{}\nbut it was:\n{}\n" \
        .format(common_scanpath_expected, common_scanpath_actual)


def test_run_emine_and_expect_empty_common_scanpath():
    raw_sequences = {
        'P01': [['A', 100], ['B', 100]],
        'P02': [['C', 100], ['D', 100]]
    }

    common_scanpath_expected = {
        'identifier': 'eMINE',
        'fixations': [],
        'similarity': {}
    }

    common_scanpath_actual = emine.run_emine(raw_sequences)

    assert common_scanpath_actual == common_scanpath_expected, \
        "Wrong output for the non-existing common scanpath"


def test_run_emine_with_empty_scanpaths_list():
    raw_sequences = {}

    common_scanpath_expected = {
        'identifier': 'eMINE',
        'fixations': [],
        'similarity': {}
    }

    common_scanpath_actual = emine.run_emine(raw_sequences)

    assert common_scanpath_actual == common_scanpath_expected, \
        "Wrong output for the non-existing common scanpath"
