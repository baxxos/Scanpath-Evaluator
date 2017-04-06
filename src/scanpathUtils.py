from __future__ import division

import math

from models.Environment import Environment
from stringEditAlgs import *

# TODO scanpaths & visuals are for one page (dataset -> template_sta). Change to dataset -> template_sta -> first_screen
# Environment in which the eye tracking experiment was performed
recording_env = Environment(0.5, 60, 1920, 1080, 17)


def createSequences(Participants, myAoIs, errorRateArea):
    # LEGACY CODE downloaded from the STA research paper
    Sequences = {}
    for participant_id in Participants:
        # An individual sequence/scanpath
        sequence = ''
        # For simplifying/normalizing the scanpaths ('AAABBBC' -> 'ABC')
        prev_aoi = ''
        prev_duration = 0
        prev_total_duration = 0
        for fixation in Participants[participant_id]:
            temp_aoi = ''
            temp_duration = 0
            for act_aoi in myAoIs:
                if float(fixation[3]) >= (act_aoi[1] - errorRateArea) and \
                        float(fixation[3]) < ((act_aoi[1] - errorRateArea) + (act_aoi[2] + 2 * errorRateArea)) and \
                        float(fixation[4]) >= (act_aoi[3] - errorRateArea) and \
                        float(fixation[4]) < ((act_aoi[3] - errorRateArea) + (act_aoi[4] + 2 * errorRateArea)):
                    temp_aoi += act_aoi[5]
                    temp_duration = int(fixation[2])

            distanceList = []

            if len(temp_aoi) > 1:
                temp_aoi = get_closer_aoi(fixation, myAoIs, temp_aoi)
                # The code below was supposed to solve the cases when a fixation points to two AOIs at the same time.
                # However, it was causing STA to run extremely slow so we just pick the AOI that is closer.
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
                    sequence = sequence + temp_aoi[0][0] + "-" + str(temp_duration) + "."
                    prev_total_duration = temp_duration
                # If the current fixation target is the same as before then just update the duration
                else:
                    # Updated fixation duration
                    new_len = prev_total_duration + temp_duration
                    # Updated sequence string
                    sequence = sequence[0:(len(sequence) - len(str(prev_total_duration)) - 1)] + str(new_len) + '.'
                    # Save the updated values
                    prev_total_duration += temp_duration

                prev_aoi = temp_aoi[0][0]
                prev_duration = temp_duration

        Sequences[participant_id] = sequence

    return Sequences


def get_closer_aoi(fixation, all_aois, possible_aois):
    """
        Function helps with solving the cases when a fixation points to two AOIs at the same time - it returns
        the closer one based on distance to the corners of the 2 target AOIs.
    """
    sums_of_distances = {}
    for target_aoi in possible_aois:
        for curr_aoi in all_aois:
            if target_aoi == curr_aoi[5]:
                # Sum distance of all 4 corners
                temp_distance = []

                # up, left
                temp_distance.append(math.sqrt(pow(float(fixation[3]) - float(curr_aoi[1]), 2) +
                                               pow(float(fixation[4]) - float(curr_aoi[3]), 2)))
                # up right
                temp_distance.append(math.sqrt(pow(float(fixation[3]) - (float(curr_aoi[1]) + float(curr_aoi[2])), 2) +
                                               pow(float(fixation[4]) - float(curr_aoi[3]), 2)))
                # down left
                temp_distance.append(math.sqrt(pow(float(fixation[3]) - (float(curr_aoi[1])), 2) +
                                               pow(float(fixation[4]) - (float(curr_aoi[3]) + float(curr_aoi[4])), 2)))
                # down, right
                temp_distance.append(math.sqrt(pow(float(fixation[3]) - (float(curr_aoi[1]) + float(curr_aoi[2])), 2) +
                                               pow(float(fixation[4]) - (float(curr_aoi[3]) + float(curr_aoi[4])), 2)))
                # Push the current aoi to the list
                sums_of_distances[target_aoi] = sum(temp_distance)
                break
    # return key of minimal value in dictionary
    return min(sums_of_distances, key=sums_of_distances.get)


# Basic functionality used to load scanpath sequences and their properties in default format
def get_raw_sequences(dataset_task):
    my_error_rate_area = recording_env.get_error_rate_area()
    my_sequences = createSequences(dataset_task.participants, dataset_task.aois, my_error_rate_area)

    keys = my_sequences.keys()
    for y in range(0, len(keys)):
        my_sequences[keys[y]] = my_sequences[keys[y]].split('.')
        del my_sequences[keys[y]][len(my_sequences[keys[y]]) - 1]
    for y in range(0, len(keys)):
        for z in range(0, len(my_sequences[keys[y]])):
            my_sequences[keys[y]][z] = my_sequences[keys[y]][z].split('-')

    return my_sequences


# Alter the sequences from their default format to the desired format used on client-side
def get_task_data(dataset_task):
    raw_sequences = get_raw_sequences(dataset_task)
    formatted_sequences = dataset_task.format_sequences(raw_sequences)

    # Additional info - calculate edit distances/similarity between dataset scanpaths
    formatted_sequences = dataset_task.calc_edit_distances(formatted_sequences)
    formatted_sequences = dataset_task.calc_max_similarity(formatted_sequences)
    formatted_sequences = dataset_task.calc_min_similarity(formatted_sequences)

    # Return necessary dataset info which will be processed and rendered on the client side
    ret_dataset = {
        'scanpaths': formatted_sequences,
        'visuals': dataset_task.visuals,
        'aois': dataset_task.aois
    }

    return ret_dataset


# Reversed common scanpath algorithm - the "common" scanpath is known from the start
def run_custom(dataset_task, custom_scanpath):
    raw_sequences = get_raw_sequences(dataset_task)
    formatted_sequences = dataset_task.format_sequences(raw_sequences)

    # Store scanpaths as an array of string-converted original scanpaths
    scanpath_strs = convert_to_str_array(formatted_sequences)

    custom_scanpath_arr = []
    for i in range(0, len(custom_scanpath)):
        custom_scanpath_arr.append([custom_scanpath[i], 0])

    res_data = {
        'fixations': custom_scanpath_arr,
        'similarity': calc_similarity_to_common(scanpath_strs, custom_scanpath)
    }

    return res_data

