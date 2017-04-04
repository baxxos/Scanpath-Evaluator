from scanpathUtils import *

import copy


# eMINE algorithm (https://bop.unibe.ch/index.php/JEMR/article/view/2430)
def run_emine(dataset_task):
    my_sequences = get_raw_sequences(dataset_task)
    formatted_sequences = dataset_task.format_sequences(my_sequences)

    # Store scanpaths as an array of string-converted original scanpaths (for calculating LCS etc.)
    scanpath_strs = convert_to_str_array(formatted_sequences)
    scanpath_strs_set = copy.deepcopy(scanpath_strs)

    # For determining levenshtein distance we need a pure string version of the common scanpath ('ABC')
    common_scanpath_str = ''

    # Process until there is only 1 (common) scanpath left in the set
    while len(scanpath_strs_set):
        # Calculate the mutual similarities if there are at least 2 scanpaths in the set
        if len(scanpath_strs_set) > 1:
            calc_mutual_similarity(scanpath_strs_set)
        else:
            common_scanpath_str = scanpath_strs_set[0]['raw_str']
            break

        # Get the two most similar scanpaths
        most_similar_pair = get_most_similar_pair(scanpath_strs_set)

        lcs = get_longest_common_substring(
            most_similar_pair[0]['raw_str'],
            most_similar_pair[1]['raw_str'],
        )

        # Common scanpath does not exist
        if not lcs:
            break

        # Remove the most similar pair of scanpaths from the set
        rem_scanpath_strs_by_id(
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
        'fixations': common_scanpath_arr,
        'similarity': calc_similarity_to_common(scanpath_strs, common_scanpath_str)
    }

    return res_data
