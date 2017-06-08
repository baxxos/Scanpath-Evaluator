import ast
import os
import pandas as pd
import shutil
import string
import tempfile
import traceback

from config import config


# Utility methods to handle directory and file deletions (even if they don't exist)
def silent_dir_remove(path):
    try:
        shutil.rmtree(path)
    except OSError:
        print 'Incomplete clean up after dataset delete'
        traceback.print_exc()


def silent_file_remove(path):
    try:
        os.remove(path)
    except OSError:
        print 'Incomplete clean up after unsuccessful data parsing'
        traceback.print_exc()


def create_task_img_folder(dataset, task, file_bg_image):
    # Compose the path to the corresponding dataset static folder of the newly created task
    path_task_static_folder = os.path.join(
        'static', 'images', 'datasets',
        config['DATASET_PREFIX'] + str(dataset.id),
        config['TASK_PREFIX'] + str(task.id)
    )

    try:
        os.makedirs(path_task_static_folder)
    except OSError:
        # Raise exception only if it's something else than 'Directory already exists' error
        if not os.path.isdir(path_task_static_folder):
            raise

    # Save the background image without any content modifications
    file_bg_image.save(os.path.join(
        path_task_static_folder,
        # Save the background image with name specified in the config but keep its original extension
        config['BG_IMG_FILE']) + os.path.splitext(file_bg_image.filename)[-1]
    )


def process_scanpaths(scanpath_file, keep_cols, min_fixation_dur):
    """ Processes the input TSV file into a dictionary which is then saved into the database as JSON """

    try:
        fr = pd.read_csv(scanpath_file, sep='\t')

        # Drop the duplicate fixation values from the CSV file
        fr = fr.drop_duplicates(subset=['ParticipantName', 'FixationIndex'])

        # Keep only fixations
        if 'GazeEventType' in fr.columns:
            fr = fr[fr.GazeEventType != 'Unclassified']
            fr = fr[fr.GazeEventType != 'Saccade']

        # Keep only those lasting longer than X ms
        fr = fr[fr.GazeEventDuration > min_fixation_dur]

        # Drop fixations with negative point coordinates
        fr = fr[fr['FixationPointX (MCSpx)'] > 0]
        fr = fr[fr['FixationPointY (MCSpx)'] > 0]
        # Optional sorting
        # fr = fr.sort_values(['ParticipantName', 'FixationIndex'])

        # Keep only relevant columns
        fr = fr[keep_cols]

        # Save formatted data
        data_matrix = fr.as_matrix().tolist()

        # Object to be returned from this method
        scanpath_data = {}

        # Transform data from Pandas dataframe to a formatted Python list
        for row in data_matrix:
            participant_id = row[0]

            if participant_id not in scanpath_data:
                scanpath_data[participant_id] = []

            scanpath_data[participant_id].append(row[1:])

        return scanpath_data
    except:
        traceback.print_exc()
        raise ValueError('Failed to parse scanpath data file')


def process_aois_formatted(lines_list, sep):
    """ Converts list of TSV formatted lines into a data matrix format used by database """

    data_matrix = []

    for line in lines_list:
        # Skip empty lines
        if line.strip():
            cols = line.strip().split(sep)
            # Cast numeric values (2nd-4th column) from string to number format
            cols[1] = int(cols[1])  # AOI xFrom coord
            cols[2] = int(cols[2])  # AOI xSize
            cols[3] = int(cols[3])  # AOI yFrom coord
            cols[4] = int(cols[4])  # AOI ySize

            data_matrix.append(cols)

    return data_matrix


def process_aois(aoi_file):
    """ Handles the processing of AOI files exported from Tobii Studio in its proprietary non-structured format """

    # Line indicating that the file is structured as TSV instead of Tobii Studio export
    sep = '\t'
    tsv_file_header = 'FullName' + sep + 'XFrom' + sep + 'XSize' + sep + \
                      'YFrom' + sep + 'YSize' + sep + 'ShortName'
    # Data to be returned if the file is in the Tobii Studio format
    data_matrix = []
    # Data to be returned if the file is TSV formatted
    tsv_check_lines = []

    # Copy AOI file content into a temp file (for skipping lines etc.)
    with tempfile.TemporaryFile() as fr:
        # Copying content to the temp file & a secondary matrix used for a TSV file-type check
        for temp_line_num, temp_line in enumerate(aoi_file):
            fr.write(temp_line)

            # Skip the first line for the secondary matrix since it may contain column names instead of data
            if temp_line_num > 0:
                tsv_check_lines.append(temp_line)

        name_it = 0
        fr.seek(0)

        for line_num, line in enumerate(fr):
            line_data = line.strip().split(':')

            # Handle blank lines
            if not line.strip():
                continue
            # The file is already formatted (e.g. TSV) - return the secondary matrix
            elif line_num == 0 and line.strip() == tsv_file_header:
                return process_aois_formatted(tsv_check_lines, sep)
            # Handle AOI names
            elif line_data[0].lower().startswith('aoi'):
                act_aoi = {
                    'name': line_data[1],
                    'vertices': 0,
                    'shortName': '',
                    'expectCoords': 0
                }
            # Handle number of vertices
            elif 'vertices' in line_data[0].lower():
                if int(line_data[1]) == 4:
                    act_aoi['vertices'] = 4
                else:
                    raise ValueError('All areas of interest must have exactly 4 vertices')
            # Check for line marking coords: 'X\tY'
            elif line_data[0].startswith('X') and line_data[0].endswith('Y') and act_aoi['vertices'] == 4:
                act_aoi['expectCoords'] = 1
            # Parse coords in expected format
            elif act_aoi['expectCoords'] == 1:
                # Parse the initial coords and calculate the width/height of the AOI
                act_aoi['expectCoords'] = 0
                coords_from = line.split()

                # '222,55' -> 222.55 -> 222
                x_from = int(float(coords_from[0].replace(',', '.')))
                y_from = int(float(coords_from[1].replace(',', '.')))

                # Normalize negative values of starting points
                x_from = x_from if x_from > 0 else 0
                y_from = y_from if y_from > 0 else 0

                # Calculate X coord of the starting point and width (x_size) of the aoi
                line = next(fr)
                x_to = int(float(line.split()[0].replace(',', '.')))
                x_size = x_to - x_from

                # Fix for occasionally inconsistent data format (swapped from/to lines)
                if x_size < 0:
                    x_from, x_to = x_to, x_from  # Swaps the values of the from/to points in a pythonic way
                    x_size *= -1

                # Calculate Y coord of the starting point and height (y_size) of the aoi
                line = next(fr)
                y_to = int(float(line.split()[1].replace(',', '.')))
                y_size = y_to - y_from

                # Fix for occasionally inconsistent data format (swapped from/to lines)
                if y_size < 0:
                    y_from, y_to = y_to, y_from  # Swaps the values of the from/to points in a pythonic way
                    y_size *= -1

                if name_it < len(string.uppercase):
                    act_aoi['shortName'] = string.uppercase[name_it]
                elif name_it < (len(string.uppercase) + len(string.lowercase)):
                    act_aoi['shortName'] = string.lowercase[name_it - len(string.lowercase)]
                else:
                    # Multiple-character labeled AOIs turned out to be problematic due to string-edit algorithms
                    raise ValueError('Maximum number of AOIs (52) reached')

                data_matrix.append([
                    act_aoi['name'],
                    int(x_from), int(x_size),
                    int(y_from), int(y_size),
                    act_aoi['shortName']]
                )

                # Move to another letter of the alphabet
                name_it += 1

                # Skip last vertex (unnecessary) and move to the next AOI
                line = next(fr)
                line = next(fr)
            # Skip empty or unknown formatted lines
            else:
                continue
    # Return primary data matrix
    return data_matrix


def format_from_array(path_file_scanpaths, path_file_aois, path_file_formatted):
    """
    A one-time use function I made for converting a dataset found online into the application formatted data. The
    dataset was written in an array representation ([['A', 100], ['B', 200] ..]) and this method handles the conversion.
    It's kinda messy but might come in handy sometime.

    Args:
        path_file_aois: We need AOI file to set X/Y position for fixations (e.g. to the center of the target AOI)
        path_file_scanpaths: File containing scanpath data in an array representation
        path_file_formatted: Formatted output

    Return: Writes content of a standard Scanpaths.txt file
    """

    file_header = ['ParticipantName', 'FixationIndex', 'GazeEventType', 'GazeEventDuration',
                   'FixationPointX (MCSpx)', 'FixationPointY (MCSpx)', 'MediaName']
    sep = '\t'

    with open(path_file_formatted, 'w') as fw:
        with open(path_file_scanpaths, 'r') as fr_scanpaths:
            # Write table headers divided by separator (except for the last one)
            for index, column in enumerate(file_header):
                fw.write(column + '\n' if index == (len(file_header) - 1) else column + sep)

            # Set IDs for participants
            participant_id = 1

            # Each line contains exactly one nested array containing fixations of one participant
            for line in fr_scanpaths:
                # Load the array stored as string into a real Python array
                fixations = ast.literal_eval(line)
                # Keeping track of the fixation index
                fixation_index = 1.0

                for fixation in fixations:
                    line_to_write = ('ID' + str(participant_id) + '\t') if participant_id > 9 else ('ID0' + str(
                        participant_id) + '\t')
                    line_to_write += (str(fixation_index) + '\t' + 'Fixation' + '\t')
                    line_to_write += (fixation[1] + '\t')

                    fixation_xpos = ''
                    fixation_ypos = ''

                    with open(path_file_aois, 'r') as fr_aois:
                        # Skip the heading row
                        aoi = next(fr_aois)

                        for aoi in fr_aois:
                            aoi_data = aoi.rstrip().split('\t')

                            if aoi_data[-1] == fixation[0]:
                                # Set the fixation coords as the center of the enclosing AOI
                                fixation_xpos = (int(aoi_data[1]) + (int(aoi_data[2]) / 2))
                                fixation_ypos = (int(aoi_data[3]) + (int(aoi_data[4]) / 2))
                                break

                        # Compose the final line format
                        line_to_write += (str(float(int(fixation_xpos))) + '\t')
                        line_to_write += (str(float(int(fixation_ypos))) + '\t')
                        line_to_write += 'N/A\n'
                        # Write & continue
                        fw.write(line_to_write)
                        fixation_index += 1

                participant_id += 1
