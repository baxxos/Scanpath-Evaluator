from __future__ import division

import math
import traceback

import src.stringEditAlgs as seAlg


# *** Scanpath composing ***
def create_initial_sequences(participants, aois, error_rate_area):
    """
    Default method for converting raw sequence data loaded from a TSV-ish format into a temporary string representation:
    Input:
        {
            'ID02': [
                ['0.0', 'Fixation', '150', '557', '40'],
                ['1.0', 'Fixation', '600', '478', '159'],
                ['2.0', 'Fixation', '300', '499', '300']
                ],
            'ID03': ...
        }
    Output: { 'ID02': 'A-150.B-600.C-300.', 'ID03': ... }
     """

    # LEGACY CODE downloaded from the STA research paper
    my_sequences = {}
    for participant_id in participants:
        # For constructing the individual sequence (scanpath)
        sequence = ''

        # For simplifying/normalizing the scanpaths ('AAABBBC' -> 'ABC')
        prev_aoi = ''
        prev_duration, prev_total_duration = 0, 0

        for fixation in participants[participant_id]:
            temp_aoi = ''
            fixation_duration = 0

            for act_aoi in aois:
                # Save the fixation coordinates
                fixation_x, fixation_y = fixation[3], fixation[4]

                if (act_aoi[1] - error_rate_area) <= fixation_x < ((act_aoi[1] - error_rate_area) + (act_aoi[2] + 2 * error_rate_area)) and \
                        (act_aoi[3] - error_rate_area) <= fixation_y < ((act_aoi[3] - error_rate_area) + (act_aoi[4] + 2 * error_rate_area)):
                    temp_aoi += act_aoi[5]
                    fixation_duration = int(fixation[2])

            distanceList = []

            if len(temp_aoi) > 1:
                # Fixation target lies in multiple AOIs - choose the closest one
                temp_aoi = get_closer_aoi(fixation, aois, temp_aoi)

                # The code below was supposed to solve the cases when a fixation points to two AOIs at the same time.
                # However, it was causing STA to run extremely slow so we just pick the closest AOI.
                """
                for m in temp_aoi:
                    for n in range(0, len(myAoIs)):
                        if m == myAoIs[n][5]:
                            distance = []
                            for s in range(int(myAoIs[n][1]), int(myAoIs[n][1]) + int(myAoIs[n][2])):
                                for f in range(int(myAoIs[n][3]), int(myAoIs[n][3]) + int(myAoIs[n][4])):
                                    distance.append(math.sqrt(pow(float(fixation[3]) - s, 2) + pow(
                                        float(fixation[4]) - f, 2)))
                            distanceList.append([myAoIs[n][5], min(distance)])
                distanceList.sort(key=lambda x: x[1])
                temp_aoi = distanceList[0][0]
                """
            if len(temp_aoi) == 1:
                # If the current fixation target is a different AOI than the one before
                if prev_aoi != temp_aoi[0][0]:
                    sequence = sequence + temp_aoi[0][0] + "-" + str(fixation_duration) + "."
                    prev_total_duration = fixation_duration
                # If the current fixation target is the same as before then just update the duration
                else:
                    # Updated fixation duration
                    new_len = prev_total_duration + fixation_duration
                    # Updated sequence string
                    sequence = sequence[0:(len(sequence) - len(str(prev_total_duration)) - 1)] + str(new_len) + '.'
                    # Save the updated values
                    prev_total_duration += fixation_duration

                prev_aoi = temp_aoi[0][0]
                prev_duration = fixation_duration

        my_sequences[participant_id] = sequence

    return my_sequences


def get_closer_aoi(fixation, all_aois, possible_aois):
    """
    Function helps with solving the cases when a fixation points to two AOIs at the same time - it returns
    the closer one based on distance to the corners of the 2 target AOIs.
    """
    fixation_x, fixation_y = float(fixation[3]), float(fixation[4])

    sums_of_distances = {}
    for target_aoi in possible_aois:
        for curr_aoi in all_aois:
            if target_aoi == curr_aoi[5]:
                aoi_x, aoi_width = float(curr_aoi[1]), float(curr_aoi[2])
                aoi_y, aoi_height = float(curr_aoi[3]), float(curr_aoi[4])

                # Sum distance of all 4 corners
                temp_distance = []

                # up, left
                temp_distance.append(math.sqrt(pow(fixation_x - aoi_x, 2) +
                                               pow(fixation_y - aoi_y, 2)))
                # up right
                temp_distance.append(math.sqrt(pow(fixation_x - (aoi_x + aoi_width), 2) +
                                               pow(fixation_y - aoi_y, 2)))
                # down left
                temp_distance.append(math.sqrt(pow(fixation_x - aoi_x, 2) +
                                               pow(fixation_y - (aoi_y + aoi_height), 2)))
                # down, right
                temp_distance.append(math.sqrt(pow(fixation_x - (aoi_x + aoi_width), 2) +
                                               pow(fixation_y - (aoi_y + aoi_height), 2)))
                # Push the current aoi to the list
                sums_of_distances[target_aoi] = sum(temp_distance)
                break

    # return key of minimal value in dictionary
    return min(sums_of_distances, key=sums_of_distances.get)


# Basic functionality used to load scanpath sequences and their properties in default format
# TODO the DatasetTask format has changed - participants/aois are stored in the DB, pass them as attributes instead
# TODO also pass sequences as attribute
def get_raw_sequences(dataset_task):
    """
    Converts the string represented sequences to a sensible dict of arrays: {'ID1': [['F', '383'], ['G', '150']], .. }
    """

    # Try to set error rate area (set to 0 if any parameters are missing)
    try:
        my_error_rate_area = dataset_task.dataset.get_error_rate_area()
    except:
        traceback.print_exc()
        my_error_rate_area = 0

    my_sequences = create_initial_sequences(dataset_task.scanpath_data_raw, dataset_task.aoi_data, my_error_rate_area)

    keys = my_sequences.keys()
    # String gets split into an array: ['G-138', 'C-184']
    for y in range(0, len(keys)):
        my_sequences[keys[y]] = my_sequences[keys[y]].split('.')
        del my_sequences[keys[y]][len(my_sequences[keys[y]]) - 1]
    # Array string elements get split into an AOI-duration pairs: ['G', 138]
    for y in range(0, len(keys)):
        for z in range(0, len(my_sequences[keys[y]])):
            my_sequences[keys[y]][z] = my_sequences[keys[y]][z].split('-')
            my_sequences[keys[y]][z][1] = int(my_sequences[keys[y]][z][1])  # Cast the fixation duration to a number

    return my_sequences


# TODO don't pass whole task object as an attribute, only sequences
def get_formatted_sequences(dataset_task):
    raw_sequences = get_raw_sequences(dataset_task)
    formatted_sequences = dataset_task.format_sequences(raw_sequences)

    # Additional info - calculate edit distances/similarity between dataset scanpaths
    formatted_sequences = calc_edit_distances(formatted_sequences)
    formatted_sequences = calc_max_similarity(formatted_sequences)
    formatted_sequences = calc_min_similarity(formatted_sequences)

    return formatted_sequences


# *** Similarity calculations ***
def calc_max_similarity(scanpaths):
    """ Function calculates most similar pair for each scanpath in the set """
    for scanpath in scanpaths:
        # Create empty max_similarity object
        max_similar = {
            'identifier':  '',
            'value': -1
        }
        # Iterate through previously calculated similarity values of given scanpath
        for similarity_iter in scanpath['similarity']:
            similarity_val = scanpath['similarity'][similarity_iter]
            if similarity_val > max_similar['value']:
                max_similar['value'] = similarity_val
                max_similar['identifier'] = similarity_iter
        # Assign max_similarity object to scanpath (in JSON-style)
        scanpath['maxSimilarity'] = max_similar

    return scanpaths


def calc_min_similarity(scanpaths):
    """ Function calculates least similar pair for each scanpath in the set """
    for scanpath in scanpaths:
        # Create empty max_similarity object
        min_similar = {
            'identifier': '',
            'value': 101
        }
        # Iterate through previously calculated similarity values of given scanpath
        for similarity_iter in scanpath['similarity']:
            similarity_val = scanpath['similarity'][similarity_iter]
            if similarity_val < min_similar['value']:
                min_similar['value'] = similarity_val
                min_similar['identifier'] = similarity_iter
        # Assign max_similarity object to scanpath (in JSON-style)
        scanpath['minSimilarity'] = min_similar

    return scanpaths


def calc_edit_distances(scanpaths):
    # Store scanpaths as an array of string-converted original scanpaths
    scanpath_strs = seAlg.convert_to_str_array(scanpaths)

    # Calculate the edit distances
    # The order of records in scanpaths and scanpath_strs must be the same!
    seAlg.calc_mutual_similarity(scanpath_strs)

    for i_first in range(0, len(scanpath_strs)):
        # Save the calculations to the original scanpaths object
        scanpaths[i_first]['similarity'] = scanpath_strs[i_first]['similarity']

    return scanpaths


# *** Custom runs ***
def run_custom(dataset_task, custom_scanpath):
    """ Reversed common scanpath algorithm - the "common" scanpath is known from the start. """

    raw_sequences = get_raw_sequences(dataset_task)
    formatted_sequences = dataset_task.format_sequences(raw_sequences)

    # Store scanpaths as an array of string-converted original scanpaths
    scanpath_strs = seAlg.convert_to_str_array(formatted_sequences)

    custom_scanpath_arr = []
    for i in range(0, len(custom_scanpath)):
        custom_scanpath_arr.append([custom_scanpath[i], 0])

    res_data = {
        'identifier': 'custom',
        'fixations': custom_scanpath_arr,
        'similarity': seAlg.calc_similarity_to_common(scanpath_strs, custom_scanpath)
    }

    return res_data


def run_empty(alg_name):
    """
    Generates an empty (dummy) scanpath algorithm result. Used for excluding selected algorithms during
    algorithm cross-comparisons.
    """

    return {
        'identifier': alg_name,
        'fixations': [],
        'similarity': {},
        'excluded': True
    }



