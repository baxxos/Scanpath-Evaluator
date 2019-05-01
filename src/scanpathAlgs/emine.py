import copy

import src.scanpathUtils as spUtil
import src.stringEditAlgs as seAlg


def simplify_scanpath(scanpath):
    res_str = ''

    for i in range(0, len(scanpath)):
        if i == 0:
            res_str += scanpath[i]
        elif i > 0 and scanpath[i] != scanpath[i - 1]:
            res_str += scanpath[i]

    return res_str


# eMINE algorithm (https://bop.unibe.ch/index.php/JEMR/article/view/2430)
def run_emine(raw_sequences):
    """
    Args:
        raw_sequences: a Python dict of lists - {'ID1': [['F', '383'], ['G', '150']], 'ID2': .. }
    Returns:
        identifier: for client-side purposes
        fixations: a list of lists representing the common scanpath - [['A', 150], ['B', 500] .. ]
        similarity: a dict containing similarity of individual scanpaths to the common one - {'ID1': 66.66, 'ID2': ... }
    """
    formatted_sequences = spUtil.format_sequences(raw_sequences)

    # Store scanpaths as an array of string-converted original scanpaths (for calculating LCS etc.)
    scanpath_strs = seAlg.convert_to_str_array(formatted_sequences)
    scanpath_strs_set = copy.deepcopy(scanpath_strs)

    # For determining get_edit_distance distance we need a pure string version of the common scanpath ('ABC')
    common_scanpath_str = ''

    # Process until there is only 1 (common) scanpath left in the set
    while len(scanpath_strs_set):
        # Calculate the mutual similarities if there are at least 2 scanpaths in the set
        if len(scanpath_strs_set) > 1:
            seAlg.calc_mutual_similarity(scanpath_strs_set)
        else:
            common_scanpath_str = simplify_scanpath(scanpath_strs_set[0]['raw_str'])
            break

        # Get the two most similar scanpaths
        most_similar_pair = seAlg.get_most_similar_pair(scanpath_strs_set)

        lcs = seAlg.get_longest_common_subsequence(
            most_similar_pair[0]['raw_str'],
            most_similar_pair[1]['raw_str'],
        )

        # Common scanpath does not exist
        if not lcs:
            break

        # Remove the most similar pair of scanpaths from the set
        seAlg.rem_scanpath_strs_by_id(
            scanpath_strs_set,
            [most_similar_pair[0]['identifier'], most_similar_pair[1]['identifier']]
        )
        # Insert their longest common substring instead
        scanpath_strs_set.append({
            'raw_str': lcs,
            'identifier': most_similar_pair[0]['identifier']
        })

    common_scanpath_arr = []
    for i in range(0, len(common_scanpath_str)):
        common_scanpath_arr.append([common_scanpath_str[i], 0])

    res_data = {
        'identifier': 'eMINE',
        'fixations': common_scanpath_arr,
        'similarity': seAlg.calc_similarity_to_common(scanpath_strs, common_scanpath_str)
    }

    return res_data
