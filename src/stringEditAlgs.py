from __future__ import division


def convert_to_str_array(scanpaths):
    """
    Converts the dict-formatted scanpaths into an array of strings for similarity calculations. Even though an array is
    not good for searching scanpath by IDs (O(n) time), it provides an easy way to get the size, n-th element or index.

    From: [{'fixations': [['A', '150'], ['B', '750'], ['C', '300']], 'identifier': '02'}, ..]
    To: [{'raw_str': 'ABC', 'identifier': '02'}, {'raw_str': 'AC', 'identifier': '03'}, .. ]
     """

    scanpath_strs = []
    # Extract scanpaths as raw string sequences with identifiers
    for act_scanpath in scanpaths:
        act_scanpath_str = ''
        for fixation in act_scanpath['fixations']:
            act_scanpath_str += fixation[0]
        # Store the identifier and extracted string sequence in an object
        temp_scanpath = {
            'identifier': act_scanpath['identifier'],
            'raw_str': act_scanpath_str
        }
        # Push the object to the array
        scanpath_strs.append(temp_scanpath)

    return scanpath_strs


def calc_similarity(scanpath1, scanpath2):
    """ Calculates similarity between two scanpath strings represented as percentage. """

    # Calculate the similarity value based on the edit distance of given scanpaths
    edit_distance = get_edit_distance(scanpath1, scanpath2)
    similarity = 1 - (edit_distance / (len(scanpath1) if len(scanpath1) > len(scanpath2) else len(scanpath2)))

    # Return similarity as percentage
    return similarity * 100


def calc_mutual_similarity(scanpath_strs):
    """ Calculates mutual similarity between all scanpaths of the formatted array. """

    for i_first in range(0, len(scanpath_strs)):
        # Each scanpath has a similarity object - similarity[id] represents
        # the level of similarity to the scanpath identified by id
        scanpath1 = scanpath_strs[i_first]

        # If the similarity object of first scanpath does not exist yet - create it
        if not scanpath1.get('similarity'):
            scanpath1['similarity'] = {}

        for i_second in range(i_first + 1, len(scanpath_strs)):
            scanpath2 = scanpath_strs[i_second]

            # Get the IDs of the current scanpath pair
            identifier_first = scanpath1['identifier']
            identifier_second = scanpath2['identifier']

            # Performance boost: skip if the similarity between current scanpath pair has already been calculated
            if scanpath1.get('similarity') and scanpath1['similarity'].get(identifier_second) and \
                    scanpath2.get('similarity') and scanpath2['similarity'].get(identifier_first):
                continue

            similarity = calc_similarity(scanpath1['raw_str'], scanpath2['raw_str'])

            # Set the similarity for the first scanpath
            scanpath1['similarity'][identifier_second] = similarity

            # If the similarity object of second scanpath does not exist yet - create it
            if not scanpath2.get('similarity'):
                scanpath2['similarity'] = {}

            # Set the same similarity as above for the second scanpath
            scanpath2['similarity'][identifier_first] = similarity


def calc_similarity_to_common(scanpath_strs, scanpath_common):
    """ Calculates similarity of each individual scanpath to the common one based on the defined similarity formula. """

    # Object storing similarities of each individual scanpath to the common one
    similarity_obj = {}
    len_common = len(scanpath_common)

    # If the common scanpath is not empty (there are cases of no common scanpath sometimes)
    if len_common:
        # Calculate similarity of each scanpath to the common (trending) scanpath
        for scanpath_str in scanpath_strs:
            similarity = calc_similarity(scanpath_common, scanpath_str['raw_str'])
            similarity_obj[scanpath_str['identifier']] = similarity

    return similarity_obj


def get_most_similar_pair(scanpath_strs):
    """ Method looks for the most similar pair of scanpath strings in the given set. """

    most_similar_pair = [scanpath_strs[0], scanpath_strs[0], -1]

    for scanpath in scanpath_strs:
        for scanpath_id in scanpath['similarity']:
            if scanpath['similarity'][scanpath_id] > most_similar_pair[2]:
                most_similar_pair = [
                    scanpath,
                    get_scanpath_str_by_id(scanpath_strs, scanpath_id),
                    scanpath['similarity'][scanpath_id]
                ]

    return most_similar_pair


def get_scanpath_str_by_id(scanpath_strs, identifier):
    """
    Since scanpaths are stored as an array of dicts (might be changed to a dict of dicts later), sometimes
    we need this function to fetch us a particular scanpath by its id.
    """

    for scanpath in scanpath_strs:
        if scanpath['identifier'] == identifier:
            return scanpath

    raise LookupError('No such identifier in scanpath strings array: ' + identifier)


def rem_scanpath_strs_by_id(scanpath_strs, ids_to_rem):
    """
    Function removes scanpaths from the list based on provided ids. It also deletes any references to
    these scanpaths from the existing similarity objects of remaining scanpaths.
    """

    # Delete scanpaths specified by id
    for identifier in ids_to_rem:
        scanpath_strs.remove(get_scanpath_str_by_id(scanpath_strs, identifier))

    # Delete existing references to previously deleted scanpaths
    for scanpath in scanpath_strs:
        for identifier in ids_to_rem:
            if scanpath.get('similarity') and identifier in scanpath['similarity']:
                scanpath['similarity'].pop(identifier, None)


def clear_mutual_similarity(scanpath_strs):
    """ Clears the similarity object of all scanpaths in the array. """

    for scanpath in scanpath_strs:
        scanpath.pop('similarity', None)


def get_longest_common_substring(s1, s2):
    # Source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring

    m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
    longest, x_longest = 0, 0

    for x in xrange(1, 1 + len(s1)):
        for y in xrange(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0

    return s1[x_longest - longest: x_longest]


def get_longest_common_subsequence(s1, s2):
    # Source: https://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_8

    lengths = [[0 for j in range(len(s2) + 1)] for i in range(len(s1) + 1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(s1):
        for j, y in enumerate(s2):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])

    # read the substring out from the matrix
    result = ""
    x, y = len(s1), len(s2)

    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert s1[x - 1] == s2[y - 1]
            result = s1[x - 1] + result
            x -= 1
            y -= 1

    return result


def get_edit_distance(s1, s2):
    # Source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance

    if len(s1) < len(s2):
        return get_edit_distance(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer than s2
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)

            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
