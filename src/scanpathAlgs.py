from __future__ import division
from DatasetTask import DatasetTask
from Environment import Environment
from stringEditAlgs import *

import copy

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


def getNumberedSequence(Sequence, dataset_task):
    numberedSequence = []
    numberedSequence.append([Sequence[0][0], 1, Sequence[0][1]])

    for y in range(1, len(Sequence)):
        if Sequence[y][0] == Sequence[y - 1][0]:
            numberedSequence.append([Sequence[y][0], numberedSequence[len(numberedSequence) - 1][1], Sequence[y][1]])
        else:
            numberedSequence.append([Sequence[y][0], getSequenceNumber(Sequence[0:y], Sequence[y][0]), Sequence[y][1]])

    AoIList = getExistingAoIListForSequence(numberedSequence)
    AoINames = dataset_task.aois
    AoINames = [w[5] for w in AoINames]
    newSequence = []

    myList = []
    myDictionary = {}
    replacementList = []

    for x in range(0, len(AoIList)):
        totalDuration = 0
        for y in range(0, len(numberedSequence)):
            if numberedSequence[y][0:2] == AoIList[x]:
                totalDuration = totalDuration + int(numberedSequence[y][2])
        myList.append([AoIList[x], totalDuration])

    for x in range(0, len(AoINames)):
        myAoIList = [w for w in myList if w[0][0] == AoINames[x]]
        myAoIList.sort(key=lambda x: x[1])
        myAoIList.reverse()
        if len(myAoIList) > 0:
            myDictionary[AoINames[x]] = myAoIList

    for AoI in AoIList:
        index = [w[0] for w in myDictionary[AoI[0]]].index(AoI)
        replacementList.append([AoI, [AoI[0], (index + 1)]])

    for x in range(0, len(numberedSequence)):
        myReplacementList = [w[0] for w in replacementList]
        index = myReplacementList.index(numberedSequence[x][0:2])
        newSequence.append([replacementList[index][1][0]] + [replacementList[index][1][1]] + [numberedSequence[x][2]])

    return newSequence


def getSequenceNumber(Sequence, Item):
    abstractedSequence = getAbstractedSequence(Sequence)
    return abstractedSequence.count(Item) + 1


def getAbstractedSequence(Sequence):
    myAbstractedSequence = [Sequence[0]]
    for y in range(1, len(Sequence)):
        if myAbstractedSequence[len(myAbstractedSequence) - 1] != Sequence[y][0]:
            myAbstractedSequence.append([Sequence[y][0], Sequence[y][1]])
    return myAbstractedSequence


def getExistingAoIListForSequence(Sequence):
    AoIlist = []
    for x in range(0, len(Sequence)):
        try:
            AoIlist.index(Sequence[x][0:2])
        except:
            AoIlist.append(Sequence[x][0:2])
    return AoIlist


def calculateImportanceThreshold(mySequences):
    myAoICounter = getNumberDurationOfAoIs(mySequences)
    commonAoIs = []
    for myAoIdetail in myAoICounter:
        if myAoIdetail[3] == True:
            commonAoIs.append(myAoIdetail)

    if len(commonAoIs) == 0:
        print "No shared instances!"
        exit(1)

    minValueCounter = commonAoIs[0][1]
    for AoIdetails in commonAoIs:
        if minValueCounter > AoIdetails[1]:
            minValueCounter = AoIdetails[1]

    minValueDuration = commonAoIs[0][2]
    for AoIdetails in commonAoIs:
        if minValueDuration > AoIdetails[2]:
            minValueDuration = AoIdetails[2]

    return [minValueCounter, minValueDuration]


def getNumberDurationOfAoIs(Sequences):
    AoIs = getExistingAoIList(Sequences)
    AoIcount = []
    for x in range(0, len(AoIs)):
        counter = 0
        duration = 0
        flagCounter = 0
        keys = Sequences.keys()
        for y in range(0, len(keys)):
            if [s[0:2] for s in Sequences[keys[y]]].count(AoIs[x]) > 0:
                counter = counter + [s[0:2] for s in Sequences[keys[y]]].count(AoIs[x])
                duration = duration + sum([int(w[2]) for w in Sequences[keys[y]] if w[0:2] == AoIs[x]])
                flagCounter = flagCounter + 1

        if flagCounter >= len(keys) / 2:
            AoIcount.append([AoIs[x], counter, duration, True])
        else:
            AoIcount.append([AoIs[x], counter, duration, False])
    return AoIcount


def updateAoIsFlag(AoIs, threshold):
    for AoI in AoIs:
        if AoI[1] >= threshold[0] and AoI[2] >= threshold[1]:
            AoI[3] = True
    return AoIs


def removeInsignificantAoIs(Sequences, AoIList):
    significantAoIs = []
    for AoI in AoIList:
        if AoI[3] == True:
            significantAoIs.append(AoI[0])

    keys = Sequences.keys()
    for y in range(0, len(keys)):
        temp = []
        for k in range(0, len(Sequences[keys[y]])):
            try:
                significantAoIs.index(Sequences[keys[y]][k][0:2])
                temp.append(Sequences[keys[y]][k])
            except:
                continue
        # Fix for scanpaths consisting only from insignificant aois - remove such scanpaths
        if len(temp) > 0:
            Sequences[keys[y]] = temp
        else:
            Sequences.pop(keys[y], None)
    return Sequences


def getExistingAoIList(Sequences):
    AoIlist = []
    keys = Sequences.keys()
    for y in range(0, len(keys)):
        for x in range(0, len(Sequences[keys[y]])):
            try:
                AoIlist.index(Sequences[keys[y]][x][0:2])
            except:
                AoIlist.append(Sequences[keys[y]][x][0:2])
    return AoIlist


def calculateNumberDurationOfFixationsAndNSV(Sequences):
    keys = Sequences.keys()
    for x in range(0, len(keys)):
        myAbstractedSequence = []
        myAbstractedSequence = [Sequences[keys[x]][0][0:2] + [1] + [int(Sequences[keys[x]][0][2])]]
        for y in range(1, len(Sequences[keys[x]])):
            if myAbstractedSequence[len(myAbstractedSequence) - 1][0:2] != Sequences[keys[x]][y][0:2]:
                myAbstractedSequence.append(Sequences[keys[x]][y][0:2] + [1] + [int(Sequences[keys[x]][y][2])])
            else:
                myAbstractedSequence[len(myAbstractedSequence) - 1][2] = \
                myAbstractedSequence[len(myAbstractedSequence) - 1][2] + 1
                myAbstractedSequence[len(myAbstractedSequence) - 1][3] = \
                myAbstractedSequence[len(myAbstractedSequence) - 1][3] + int(Sequences[keys[x]][y][2])

        Sequences[keys[x]] = myAbstractedSequence

    keys = Sequences.keys()

    for x in range(0, len(keys)):
        for y in range(0, len(Sequences[keys[x]])):
            if len(Sequences[keys[x]]) < 2:
                value = 0
            else:
                value = 0.9 / (len(Sequences[keys[x]]) - 1)
            NSV = 1 - round(y, 2) * value
            Sequences[keys[x]][y] = Sequences[keys[x]][y] + [NSV]
    return Sequences


def calculateTotalNumberDurationofFixationsandNSV(AoIList, Sequences):
    for x in range(0, len(AoIList)):
        duration = 0
        counter = 0
        totalNSV = 0

        flag = 0
        keys = Sequences.keys()
        for y in range(0, len(keys)):
            for k in range(0, len(Sequences[keys[y]])):
                if Sequences[keys[y]][k][0:2] == AoIList[x]:
                    counter += Sequences[keys[y]][k][2]
                    duration += Sequences[keys[y]][k][3]
                    totalNSV += Sequences[keys[y]][k][4]
                    flag += 1
        if flag >= len(Sequences) / 2:
            AoIList[x] = AoIList[x] + [counter] + [duration] + [totalNSV] + [True]
        else:
            AoIList[x] = AoIList[x] + [counter] + [duration] + [totalNSV] + [False]

    return AoIList


def getValueableAoIs(AoIList):
    commonAoIs = []
    valuableAoIs = []
    for myAoIdetail in AoIList:
        if myAoIdetail[5] == True:
            commonAoIs.append(myAoIdetail)

    minValue = commonAoIs[0][4]
    for AoIdetails in commonAoIs:
        if minValue > AoIdetails[4]:
            minValue = AoIdetails[4]

    for myAoIdetail in AoIList:
        if myAoIdetail[4] >= minValue:
            valuableAoIs.append(myAoIdetail)

    return valuableAoIs


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


# STA Algorithm
def run_sta(dataset_task):
    # Preliminary Stage
    mySequences = get_raw_sequences(dataset_task)

    # First-Pass
    mySequences_num = {}
    keys = mySequences.keys()
    for y in range(0, len(keys)):
        mySequences_num[keys[y]] = getNumberedSequence(mySequences[keys[y]], dataset_task)

    myImportanceThreshold = calculateImportanceThreshold(mySequences_num)
    myImportantAoIs = updateAoIsFlag(getNumberDurationOfAoIs(mySequences_num), myImportanceThreshold)
    myNewSequences = removeInsignificantAoIs(mySequences_num, myImportantAoIs)

    # Second-Pass
    myNewAoIList = getExistingAoIList(myNewSequences)
    myNewAoIList = calculateTotalNumberDurationofFixationsandNSV(myNewAoIList,
                                                                 calculateNumberDurationOfFixationsAndNSV(myNewSequences))
    myFinalList = getValueableAoIs(myNewAoIList)

    myFinalList.sort(key=lambda x: (x[4], x[3], x[2]))
    myFinalList.reverse()

    commonSequence = []

    for y in range(0, len(myFinalList)):
        commonSequence.append([myFinalList[y][0], int(myFinalList[y][3] / myFinalList[y][2])])

    formatted_sequences = dataset_task.format_sequences(mySequences)

    # Store scanpaths as an array of string-converted original scanpaths
    scanpath_strs = convert_to_strs(formatted_sequences)

    common_scanpath = getAbstractedSequence(commonSequence)
    common_scanpath_str = ''

    # For determining levenshtein distance we need a pure string version of the common scanpath ('ABC')
    for fixation in common_scanpath:
        common_scanpath_str += fixation[0]

    res_data = {
        'fixations': common_scanpath,
        'similarity': calc_similarity_to_common(scanpath_strs, common_scanpath_str)
    }

    return res_data


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


# eMINE algorithm (https://bop.unibe.ch/index.php/JEMR/article/view/2430)
def run_emine(dataset_task):
    my_sequences = get_raw_sequences(dataset_task)
    formatted_sequences = dataset_task.format_sequences(my_sequences)

    # Store scanpaths as an array of string-converted original scanpaths (for calculating LCS etc.)
    scanpath_strs = convert_to_strs(formatted_sequences)
    scanpath_strs_unmodified = copy.deepcopy(scanpath_strs)

    # For determining levenshtein distance we need a pure string version of the common scanpath ('ABC')
    common_scanpath_str = ''

    # Process until there is only 1 (common) scanpath left in the set
    while len(scanpath_strs):
        # Calculate the mutual similarities if there are at least 2 scanpaths in the set
        if len(scanpath_strs) > 1:
            calc_mutual_similarity(scanpath_strs)
        else:
            common_scanpath_str = scanpath_strs[0]['raw_str']
            break

        # Get the two most similar scanpaths
        most_similar_pair = get_most_similar_pair(scanpath_strs)

        lcs = get_longest_common_substring(
            most_similar_pair[0]['raw_str'],
            most_similar_pair[1]['raw_str'],
        )

        # Common scanpath does not exist
        if not lcs:
            break

        # Remove the most similar pair of scanpaths from the set
        rem_scanpath_strs_by_id(
            scanpath_strs,
            [most_similar_pair[0]['identifier'], most_similar_pair[1]['identifier']]
        )
        # Insert their longest common substring instead
        scanpath_strs.append({
            'raw_str': lcs,
            'identifier': most_similar_pair[0]['identifier']
        })

    common_scanpath_arr = []
    for i in range(0, len(common_scanpath_str)):
        common_scanpath_arr.append([common_scanpath_str[i], 0])

    res_data = {
        'fixations': common_scanpath_arr,
        'similarity': calc_similarity_to_common(scanpath_strs_unmodified, common_scanpath_str)
    }

    return res_data
