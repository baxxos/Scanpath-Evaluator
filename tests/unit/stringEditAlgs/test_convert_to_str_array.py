import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))
import stringEditAlgs as stredit


def test_valid_conversion():
    input_data = [
        {'fixations': [['A', '150'], ['B', '750'], ['C', '300']], 'identifier': '01'},
        {'fixations': [['A', '150'], ['B', '750']], 'identifier': '02'}] 

    actual = stredit.convert_to_str_array(input_data)
    expected = [
        {'raw_str': 'ABC', 'identifier': '01'},
        {'raw_str': 'AB', 'identifier': '02'}]

    assert actual == expected, \
        "Scanpaths\n{}\nshould have been converted to\n{}\n, but they were converted into\n{}\ninstead" \
        .format(input, expected, actual)


def test_conversion_with_empty_scanpath():
    input_data = [
        {'fixations': [], 'identifier': '01'},
        {'fixations': [['A', '150'], ['B', '750']], 'identifier': '02'}] 

    actual = stredit.convert_to_str_array(input_data)
    expected = [
        {'raw_str': '', 'identifier': '01'},
        {'raw_str': 'AB', 'identifier': '02'}]

    assert actual == expected, \
        "Scanpaths\n{}\nshould have been converted to\n{}\n, but they were converted into\n{}\ninstead" \
        .format(input, expected, actual)