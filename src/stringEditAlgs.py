from __future__ import division


def calc_edit_distances(scanpath_strs):
    for i_first in range(0, len(scanpath_strs)):
        # Each scanpath has a similarity object - similarity[id] represents
        # the level of similarity to the scanpath identified by id

        # If the similarity object of first scanpath does not exist yet - create it
        if not scanpath_strs[i_first].get('similarity'):
            scanpath_strs[i_first]['similarity'] = {}
        for i_second in range(i_first + 1, len(scanpath_strs)):
            # Calculate the edit (Levenshtein) distance of first and second string sequence
            edit_distance = levenshtein(scanpath_strs[i_first]['raw_str'], scanpath_strs[i_second]['raw_str'])

            # Calculate similarity as edit 1 - distance/length(longer string)
            # Division operator '/' imported from Python 3.X to avoid forced integer division (use '//' instead)
            len_first = len(scanpath_strs[i_first]['raw_str'])
            len_second = len(scanpath_strs[i_second]['raw_str'])
            similarity = 1 - (edit_distance / (len_first if len_first > len_second else len_second))
            # Set similarity as percentage
            similarity *= 100

            identifier_first = scanpath_strs[i_first]['identifier']
            identifier_second = scanpath_strs[i_second]['identifier']

            # Set the similarity for the first scanpath
            scanpath_strs[i_first]['similarity'][identifier_second] = similarity

            # If the similarity object of second scanpath does not exist yet - create it
            if not scanpath_strs[i_second].get('similarity'):
                scanpath_strs[i_second]['similarity'] = {}

            # Set the same similarity as above for the second scanpath
            scanpath_strs[i_second]['similarity'][identifier_first] = similarity


def levenshtein(s1, s2):
    # Code origin is the wikipedia page of Levenshtein's distance
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1  # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]