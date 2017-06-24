import copy
import math
from operator import itemgetter

import src.scanpathUtils as spUtil
import src.stringEditAlgs as seAlg

dotplot_max_aois = 100
dotplot_error_rate_area = 0


# CODE ORIGIN: https://github.com/Groosling/DP_features_and_scanpaths
def createSequencesBasedOnVisualElements(my_dataset):
    Sequences = {}
    Participants = my_dataset.scanpath_data_raw
    myAoIs = my_dataset.aoi_data
    keys = Participants.keys()

    for y in range(0, len(keys)):
        sequence = ""
        counter = 0
        for z in range(0, len(Participants[keys[y]])):
            if counter == dotplot_max_aois:
                break
            tempAoI = ""
            tempDuration = 0

            for k in range(0, len(myAoIs)):
                if float(Participants[keys[y]][z][3]) >= (float(myAoIs[k][1]) - dotplot_error_rate_area) and float(
                        Participants[keys[y]][z][3]) < (
                ((float(myAoIs[k][1]) - dotplot_error_rate_area) + (float(myAoIs[k][2]) + 2 * dotplot_error_rate_area))) and float(
                        Participants[keys[y]][z][4]) >= (float(myAoIs[k][3]) - dotplot_error_rate_area) and float(
                        Participants[keys[y]][z][4]) < (
                ((float(myAoIs[k][3]) - dotplot_error_rate_area) + (float(myAoIs[k][4]) + 2 * dotplot_error_rate_area))):
                    tempAoI = tempAoI + myAoIs[k][5]
                    tempDuration = int(Participants[keys[y]][z][2])


            # my solution compare sum of distances to four corners
            if len(tempAoI) > 1:
                tempAoI = getCloserAOI(Participants[keys[y]][z],myAoIs, tempAoI)

            if len(tempAoI) != 0:
                counter = counter + 1
                sequence = sequence + tempAoI + "-" + str(tempDuration) + "."
                if counter == dotplot_max_aois:
                    break

        Sequences[keys[y]] = sequence
    return Sequences


def getCloserAOI(Participants_pos, myAoIs, tempAoI):
    sums_of_distances = {}
    for m in range(0, len(tempAoI)):
        for n in range(0, len(myAoIs)):
            if tempAoI[m] == myAoIs[n][5]:
                temp_distance = []
                # sum distance of all 4 corners
                # up, left
                temp_distance.append(math.sqrt(pow(float(Participants_pos[3]) - float(myAoIs[n][1]), 2) +
                                               pow(float(Participants_pos[4]) - float(myAoIs[n][3]), 2)))
                # up right
                temp_distance.append(math.sqrt(pow(float(Participants_pos[3]) - (float(myAoIs[n][1]) + float(myAoIs[n][2])), 2) +
                                               pow(float(Participants_pos[4]) - float(myAoIs[n][3]), 2)))
                # down left
                temp_distance.append(math.sqrt(pow(float(Participants_pos[3]) - (float(myAoIs[n][1])), 2) +
                                               pow(float(Participants_pos[4]) - (float(myAoIs[n][3]) + float(myAoIs[n][4])), 2)))
                # down, right
                temp_distance.append(math.sqrt(pow(float(Participants_pos[3]) - (float(myAoIs[n][1]) + float(myAoIs[n][2])), 2) +
                                               pow(float(Participants_pos[4]) - (float(myAoIs[n][3]) + float(myAoIs[n][4])), 2)))
                sums_of_distances[tempAoI[m]] = sum(temp_distance)
                break
    # return key of minimal value in dictionary
    return min(sums_of_distances, key=sums_of_distances.get)

def getArrayRepresentationOfSequence(mySequences):
    """
    Args:
        mySequences: String format of sequences

    Returns: array representation of sequence
    """
    keys = mySequences.keys()
    # odstranenie bodky na konci
    for y in range(0, len(keys)):
        mySequences[keys[y]] = mySequences[keys[y]].split('.')
        del mySequences[keys[y]][len(mySequences[keys[y]]) - 1]
    #  rozdeli D-100 na pole z dvomi prvkami D a 100
    for y in range(0, len(keys)):
        for z in range(0, len(mySequences[keys[y]])):
            mySequences[keys[y]][z] = mySequences[keys[y]][z].split('-')
    return mySequences

def simplifySequence(aSequence):
    """
    Groups same fixation in a row AAABBB ->  AB and sums up the fixDur
    Args:
        aSequence: dictionary of array representation of sequences

    Returns:
        Processed sequence in array representation
    """
    keys = aSequence.keys()
    for y in range(0, len(keys)):
        simpleSequence = []
        lastAOI = "0"
        for z in range(0, len(aSequence[keys[y]])):
            if aSequence[keys[y]][z][0] == lastAOI:
                simpleSequence[len(simpleSequence) - 1][1] = str(int(simpleSequence[len(simpleSequence) - 1][1]) + int(aSequence[keys[y]][z][1]))
            else:
                simpleSequence.append([aSequence[keys[y]][z][0], aSequence[keys[y]][z][1]])
                lastAOI = aSequence[keys[y]][z][0]
        aSequence[keys[y]] = simpleSequence
    return aSequence


def applyFixDurationThreshold(aSequence, threshold = 80):
    """
    Delete fixations shorter than defined threshold
    Args:
        aSequence: dictionary of array representation of sequences
        threshold: default 80 ms

    Returns:
        Processed sequence in array representation
    """
    keys = aSequence.keys()
    for y in range(0, len(keys)):
        processedArray = []
        for z in range(0, len(aSequence[keys[y]])):
            if int(aSequence[keys[y]][z][1]) > threshold:
                processedArray.append(aSequence[keys[y]][z])
        aSequence[keys[y]] = processedArray
    return aSequence

def getStringRepresentation(aSequence):
    """
    Returns string representation without duration of fixations
    Args:
        aSequence: dictionary of array representation of sequeces
    """
    newDict  = {}
    keys = aSequence.keys()
    for y in range(0, len(keys)):
        sequence = ""
        for z in range(0, len(aSequence[keys[y]])):
            sequence = sequence + aSequence[keys[y]][z][0]
        newDict[keys[y]] = sequence
    return newDict


def createSequencesBasedOnDistances(my_dataset):
    """
    Create Scanpath from sacade lengths(distances between fixations)
    Args:
        my_dataset: dataset
    """
    aoi_range = 300
    sequences = {}
    participants = my_dataset.scanpath_data_raw
    myAoIs = my_dataset.aoi_data
    keys = participants.keys()
    for y in range(0, len(keys)):
        sequence = ""
        for z in range(0, min(len(participants[keys[y]]) - 1, dotplot_max_aois)):
           tempdist = calculateDistance(int(float(participants[keys[y]][z][3])), int(float(participants[keys[y]][z][4])),
                                        int(float(participants[keys[y]][z + 1][3])), int(float(participants[keys[y]][z + 1][4])))
           sequence = sequence + getAOIBasedOnRange(tempdist, aoi_range) + "-" + str(int(float(participants[keys[y]][z + 1][1])) - int(float(participants[keys[y]][z][1]))) + "."
        sequences[keys[y]] = sequence
    return sequences


def calculateDistance(xStart, yStart, xEnd, yEnd):
    """
    Calculate distance of 2D coordinates.
    """
    return math.sqrt(pow(xEnd - xStart, 2) + pow(yEnd - yStart, 2))

def getAOIBasedOnRange(value, aoiRange):
    """
    Determine AOI based on range
    Args:
        value: distance between fixations
        aoiRange: range of distance for single AOI

    Returns: character representation of AOI
    """
    AOIS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return AOIS[int(value / aoiRange)]

def createSequencesBasedOnFixatonDurations(my_dataset):
    """
    Create Scanpath from fixations duration
    Args:
        my_dataset: dataset
    """
    aoi_range = 100
    sequences = {}
    participants = my_dataset.scanpath_data_raw
    myAoIs = my_dataset.aoi_data
    keys = participants.keys()
    for y in range(0, len(keys)):
        sequence = ""
        for z in range(0, min(len(participants[keys[y]]) - 1, dotplot_max_aois)):
           sequence = sequence + getAOIBasedOnRange(int(participants[keys[y]][z][2]), aoi_range) +\
                      "-" + participants[keys[y]][z][2] + "."
        sequences[keys[y]] = sequence
    return sequences


def calculateVector(xStart, yStart, xEnd, yEnd):
    """
    Calculate vector between two 2D coordinates.
    """
    return [xEnd - xStart, yEnd - yStart]


def calculateAngle(vect1, vect2):
    """
    Calculates angle between 2 vector in 2D space
    Args:
        vect1: vector represented as list
        vect2: vector represented as list
    """
    vect1Size = calculateDistance(0, 0, vect1[0], vect1[1])
    vect2Size = calculateDistance(0, 0, vect2[0], vect2[1])
    dotProduct = (vect1[0] * vect2[0]) + (vect1[1] * vect2[1])
    return math.degrees(math.acos(dotProduct / (vect1Size * vect2Size)))


def createSequencesBasedOnRelativeAngle(my_dataset):
    """
    Create Scanpath from absolute angles of saccades
    Args:
        my_dataset: dataset
    """
    aoi_range = 30
    sequences = {}
    participants = my_dataset.scanpath_data_raw
    myAoIs = my_dataset.aoi_data
    keys = participants.keys()
    for y in range(0, len(keys)):
        # TODO vec1 = vec2 at the beginning of the cycle ... better time complexity
        # TODO add condition if sequence has two elements or so.. return empty sequence.. depends ond cycle
        sequence = ""
        for z in range(0, min(len(participants[keys[y]]) - 2, dotplot_max_aois)):
            # calculates vector between curent point and next one
            vec1 = calculateVector(int(float(participants[keys[y]][z][3])), int(float(participants[keys[y]][z][4])),
                                   int(float(participants[keys[y]][z + 1][3])), int(float(participants[keys[y]][z + 1][4])))
            # calculates vector between next point and next next one
            vec2 = calculateVector(int(float(participants[keys[y]][z + 1][3])), int(float(participants[keys[y]][z + 1][4])),
                                   int(float(participants[keys[y]][z + 2][3])), int(float(participants[keys[y]][z + 2][4])))
            angle = calculateAngle(vec1, vec2)
            # duration is calculated as sum of both sacades durations
            sequence = sequence + getAOIBasedOnRange(angle, aoi_range) + "-" + str(int(float(participants[keys[y]][z + 2][1])) - int(float(participants[keys[y]][z][1]))) + "."
        sequences[keys[y]] = sequence
    return sequences


def createSequencesBasedOnAbsoluteAngle(my_dataset):
    """
    Create Scanpath from absolute angles of saccades
    Args:
        my_dataset: dataset
    """
    aoi_range = 30
    sequences = {}
    participants = my_dataset.scanpath_data_raw
    myAoIs = my_dataset.aoi_data
    keys = participants.keys()
    for y in range(0, len(keys)):
        sequence = ""
        for z in range(0, min(len(participants[keys[y]]) - 1, dotplot_max_aois)):
            # calculates vector between curent point and next one
            vec1 = calculateVector(int(float(participants[keys[y]][z][3])), int(float(participants[keys[y]][z][4])),
                                   int(float(participants[keys[y]][z + 1][3])), int(float(participants[keys[y]][z + 1][4])))
            # default vector (right direction)
            vec2 = calculateVector(0, 0, 1, 0)
            angle = calculateAngle(vec1, vec2)
            # duration is calculated as sum of both sacades durations
            sequence = sequence + getAOIBasedOnRange(angle, aoi_range) + "-" + str(int(float(participants[keys[y]][z + 1][1])) - int(float(participants[keys[y]][z][1]))) + "."
        sequences[keys[y]] = sequence
    return sequences


def create_sequences_by_mod(my_dataset, mod):
    """
    Based on mod creates sequences from dataset
    Args:
        my_dataset: dataset
        mod:     1 vytvori standardny scanpath z AOI
                 2 vytvori scanpah na zaklade dlzky sakad
                 3 vytvori scanpath na zaklade dlzky trvania fixacii
                 4 vytvori scanpath na zaklade relativnych uhlov sakad0
                 5 vytvori scanpath na zaklade absolutnych uhlov sakad
    """

    case = {
      1: createSequencesBasedOnVisualElements,
      2: createSequencesBasedOnDistances,
      3: createSequencesBasedOnFixatonDurations,
      4: createSequencesBasedOnRelativeAngle,
      5: createSequencesBasedOnAbsoluteAngle,
    }
    my_func = case[mod]
    return my_func(my_dataset)


def dotplotListofLists(sequenceX, sequenceY):
    # fill matrix with zeroes
    dotplotMatrix = [[0 for x in sequenceX] for y in sequenceY]
    # put 1 on matching positions
    for xIndex, valueX in enumerate(sequenceX):
        for yIndex, valueY in enumerate(sequenceY):
            if valueX == valueY:
                dotplotMatrix[yIndex][xIndex] = 1
    return dotplotMatrix


def findLongestCommonSequence(dotplotMatrix, sequenceX):

    commonSubSequence = ""
    lengthSubsequence = 0

    # right part of matrix
    for i in range(0, len(dotplotMatrix[0])):
        # reamining x length or height of matrix
        sum = 0
        for j in range(0, min(len(dotplotMatrix[0]) - i, len(dotplotMatrix))):
            sum += dotplotMatrix[j][i + j]

        if sum > lengthSubsequence:
            # sequence created by characters with value 1
            lengthSubsequence = sum
            commonSubSequence = ""
            for j in range(0, min(len(dotplotMatrix[0]) - i, len(dotplotMatrix))):
                if dotplotMatrix[j][i + j] == 1:
                    commonSubSequence = commonSubSequence + sequenceX[i + j]


    # left part of the matrix
    for i in range(0, len(dotplotMatrix)):
        sum = 0
        for j in range(0, min(len(dotplotMatrix) - i, len(dotplotMatrix[0]))):
            sum += dotplotMatrix[i + j][j]

        if sum > lengthSubsequence:
            # sequence created by characters with value 1
            lengthSubsequence = sum
            commonSubSequence = ""
            for j in range(0, min(len(dotplotMatrix) - i, len(dotplotMatrix[0]))):
                if dotplotMatrix[i + j][j] == 1:
                    commonSubSequence = commonSubSequence + sequenceX[j]

    return commonSubSequence


def findCommonSequence(my_str_sequences):
    """
    Finds the most similar seqecnces in dictionary and determines their common scanpath
    Args:
        my_str_sequences: dictionary of sequences in string format
    """
    string_sequences = copy.deepcopy(my_str_sequences)
    keys = string_sequences.keys()
    while len(keys) > 1:
        common_sequences = []
        for y in range(0, len(keys)):
            sequence = ""
            for z in range(y + 1, len(keys)):
                #  create matrix
                matrix = dotplotListofLists(string_sequences[keys[y]], string_sequences[keys[z]])

                # find longest common subsequence
                subSequence = findLongestCommonSequence(matrix, string_sequences[keys[y]])
                common_sequences.append([keys[y], keys[z], subSequence, len(subSequence)])

        # replace 2 most similar sequences with their common sequence
        common_sequences = sorted(common_sequences, reverse=True, key=itemgetter(3))
        if common_sequences[0][2] == '':
            return ''

        del string_sequences[common_sequences[0][0]]
        del string_sequences[common_sequences[0][1]]
        string_sequences[common_sequences[0][0] + common_sequences[0][1]] = common_sequences[0][2]
        keys = string_sequences.keys()
    return string_sequences[keys[0]]


def run_dotplot(raw_sequences, simplify=True, fix_dur_threshold=None, mod=1):
    """
    Args:
        raw_sequences: a Python dict of lists - {'ID1': [['F', '383'], ['G', '150']], 'ID2': .. }
        simplify: simplify repeated fixations on the same AOI into one
        fix_dur_threshold: minimum fixation duration threshold
        mod: 1 - vytvori standardny scanpath z AOI
             2 - vytvori scanpah na zaklade dlzky sakad (zatial nefunguje, nemame udaje o sakadach)
             3 - vytvori scanpath na zaklade dlzky trvania fixacii
             4 - vytvori scanpath na zaklade relativnych uhlov sakad (zatial nefunguje, nemame udaje o sakadach)
             5 - vytvori scanpath na zaklade absolutnych uhlov sakad (zatial nefunguje, nemame udaje o sakadach)
    Returns:
        identifier: for client-side purposes
        fixations: a list of lists representing the common scanpath - [['A', 150], ['B', 500] .. ]
        similarity: a dict containing similarity of individual scanpaths to the common one - {'ID1': 66.66, 'ID2': ... }
    """

    # The dotplot author originally provided mods for simplifying sequences and setting their min threshold
    # However, our system already does that automatically when uploading any scanpath data
    """
    my_sequences = create_sequences_by_mod(dataset_task, mod)
    my_sequences = getArrayRepresentationOfSequence(my_sequences)

    if fix_dur_threshold is not None:
        my_sequences = applyFixDurationThreshold(my_sequences, fix_dur_threshold)

    if simplify:
        my_sequences = simplifySequence(my_sequences)
    """

    string_sequences = getStringRepresentation(raw_sequences)
    common_scanpath_str = findCommonSequence(string_sequences)

    common_scanpath = []
    for fixation in common_scanpath_str:
        common_scanpath.append([fixation, 0])

    scanpath_strs = []
    for participant_id in string_sequences:
        scanpath_strs.append({
            'identifier': participant_id,
            'raw_str': string_sequences[participant_id]
        })

    res_data = {
        'identifier': 'Dotplot',
        'fixations': common_scanpath,
        'similarity': seAlg.calc_similarity_to_common(scanpath_strs, common_scanpath_str)
    }

    return res_data
