from dotplotUtil import *
from scanpathUtils import *
from stringEditAlgs import calc_similarity_to_common
from operator import itemgetter

import copy


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


def run_dotplot(dataset_task, simplify=True, fix_dur_threshold=None, mod=1):
    """
    Args:
        dataset_task: scanpath data
        simplify: urcuje ci redukovat opakujuce sa fixacie za sebou na jednu
        fix_dur_threshold: minimalna dlzka trvania fixacie
        mod: 1 vytvori standardny scanpath z AOI
             2 vytvori scanpah na zaklade dlzky sakad (zatial nefunguje, nemame udaje o sakadach)
             3 vytvori scanpath na zaklade dlzky trvania fixacii
             4 vytvori scanpath na zaklade relativnych uhlov sakad (zatial nefunguje, nemame udaje o sakadach)
             5 vytvori scanpath na zaklade absolutnych uhlov sakad (zatial nefunguje, nemame udaje o sakadach)
    """

    my_sequences = create_sequences_by_mod(dataset_task, mod)
    my_sequences = getArrayRepresentationOfSequence(my_sequences)

    if fix_dur_threshold is not None:
        my_sequences = applyFixDurationThreshold(my_sequences, fix_dur_threshold)

    if simplify:
        my_sequences = simplifySequence(my_sequences)

    string_sequences = getStringRepresentation(my_sequences)
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
        'fixations': common_scanpath,
        'similarity': calc_similarity_to_common(scanpath_strs, common_scanpath_str)
    }

    return res_data
