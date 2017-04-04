from __future__ import division
from DatasetTask import DatasetTask
from Environment import Environment
from stringEditAlgs import *


# TODO scanpaths & visuals are for one page (dataset -> template_sta). Change to dataset -> template_sta -> first_screen
# Environment in which the eye tracking experiment was performed
my_env = Environment(0.5, 60, 1920, 1080, 17)


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
            temp_aoi = []
            temp_duration = 0
            for act_aoi in myAoIs:
                if float(fixation[3]) >= (act_aoi[1] - errorRateArea) and \
                        float(fixation[3]) < ((act_aoi[1] - errorRateArea) + (act_aoi[2] + 2 * errorRateArea)) and \
                        float(fixation[4]) >= (act_aoi[3] - errorRateArea) and \
                        float(fixation[4]) < ((act_aoi[3] - errorRateArea) + (act_aoi[4] + 2 * errorRateArea)):
                    # temp_aoi.append(act_aoi[5])
                    # Workaround due to the poor quality legacy code - we need to know total area for each temp_aoi
                    # ['header', '0', '1864', '0', '90', 'Aa'] -> ['Aa', 1864 * 90]
                    temp_aoi.append([act_aoi[5], act_aoi[4] * act_aoi[2]])
                    temp_duration = int(fixation[2])

            distanceList = []

            if len(temp_aoi) > 1:
                temp_aoi.sort(key=lambda x: x[1])
                temp_aoi = temp_aoi[0][0]
                # The code below was supposed to solve the cases when a fixation points to two AOIs at the same time
                # However, it was causing STA to run extremely slow so we just pick the smaller AOI
                # This is mainly useful for hierarchy AOIs but not so much for overlapping ones
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


# Basic functionality used to load scanpath sequences and their properties in default format
def get_raw_sequences(dataset_task):
    my_error_rate_area = my_env.get_error_rate_area()
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
    scanpath_strs = convert_to_strs(formatted_sequences)

    custom_scanpath_arr = []
    for i in range(0, len(custom_scanpath)):
        custom_scanpath_arr.append([custom_scanpath[i], 0])

    res_data = {
        'fixations': custom_scanpath_arr,
        'similarity': calc_similarity_to_common(scanpath_strs, custom_scanpath)
    }

    return res_data

