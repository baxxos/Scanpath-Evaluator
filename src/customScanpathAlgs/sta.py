from scanpathUtils import *


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

        if flagCounter > len(keys) / 2:
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
    myNewAoIList = calculateTotalNumberDurationofFixationsandNSV(
        myNewAoIList,
        calculateNumberDurationOfFixationsAndNSV(myNewSequences)
    )
    myFinalList = getValueableAoIs(myNewAoIList)

    myFinalList.sort(key=lambda x: (x[4], x[3], x[2]))
    myFinalList.reverse()

    commonSequence = []

    for y in range(0, len(myFinalList)):
        commonSequence.append([myFinalList[y][0], int(myFinalList[y][3] / myFinalList[y][2])])

    formatted_sequences = dataset_task.format_sequences(mySequences)

    # Store scanpaths as an array of string-converted original scanpaths
    scanpath_strs = convert_to_str_array(formatted_sequences)

    common_scanpath = getAbstractedSequence(commonSequence)
    common_scanpath_str = ''

    # For determining get_edit_distance distance we need a pure string version of the common scanpath ('ABC')
    for fixation in common_scanpath:
        common_scanpath_str += fixation[0]

    res_data = {
        'fixations': common_scanpath,
        'similarity': calc_similarity_to_common(scanpath_strs, common_scanpath_str)
    }

    return res_data
