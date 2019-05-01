import copy
import os
import pytest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'src'))
import stringEditAlgs as stredit


def test_calc_valid_similarities():
    input_data = [
        {'raw_str': 'ABCD', 'identifier': '01'},
        {'raw_str': 'AB', 'identifier': '02'}]
    
    actual = copy.deepcopy(input_data)
    stredit.calc_mutual_similarity(actual)  # In-place modification
    expected = [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
        {'raw_str': 'AB', 'identifier': '02',  'similarity': {'01': 50}}]

    assert actual == expected, \
        "Similarity of scanpaths\n{}\nis:\n{}\n, but it should have been:\n{}" \
        .format(input_data, actual, expected)


def test_calc_similarities_if_one_scanpath_is_empty():
    input_data = [
        {'raw_str': 'ABCD', 'identifier': '01'},
        {'raw_str': '', 'identifier': '02'}]
    
    actual = copy.deepcopy(input_data)
    stredit.calc_mutual_similarity(actual)  # In-place modification
    expected = [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 0}},
        {'raw_str': '', 'identifier': '02',  'similarity': {'01': 0}}]

    assert actual == expected, \
        "Similarity of scanpaths\n{}\nis:\n{}\n, but it should have been:\n{}" \
        .format(input_data, actual, expected)



def test_calc_similarities_if_multiple_scanpaths_are_empty():
    input_data = [
        {'raw_str': 'ABCD', 'identifier': '01'},
        {'raw_str': '', 'identifier': '02'},
        {'raw_str': '', 'identifier': '03'}]
    
    actual = copy.deepcopy(input_data)
    stredit.calc_mutual_similarity(actual)  # In-place modification
    expected = [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 0, '03': 0}},
        {'raw_str': '', 'identifier': '02', 'similarity':  {'01': 0, '03': 0}},
        {'raw_str': '', 'identifier': '03',  'similarity':  {'01': 0, '02': 0}}]

    assert actual == expected, \
        "Similarity of scanpaths\n{}\nis:\n{}\n, but it should have been:\n{}" \
        .format(input_data, actual, expected)

def test_calc_similarities_if_some_of_them_are_already_precomputed():
    input_data = [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50}},
        {'raw_str': 'AB', 'identifier': '02', 'similarity': {'01': 50}},
        {'raw_str': 'A', 'identifier': '03'}]
    
    actual = copy.deepcopy(input_data)
    stredit.calc_mutual_similarity(actual)  # In-place modification
    expected = [
        {'raw_str': 'ABCD', 'identifier': '01', 'similarity': {'02': 50, '03': 25}},
        {'raw_str': 'AB', 'identifier': '02', 'similarity':  {'01': 50, '03': 50}},
        {'raw_str': 'A', 'identifier': '03',  'similarity':  {'01': 25, '02': 50}}]

    assert actual == expected, \
        "Similarity of scanpaths\n{}\nis:\n{}\n, but it should have been:\n{}" \
        .format(input_data, actual, expected)


