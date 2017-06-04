import ast
import os
import pandas as pd
import shutil
import string
import traceback

from config import config


# Utility methods to handle directory/file deletions even if they don't exist
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


def create_task_folders(dataset, task, file_aois, file_scanpaths, file_bg_image):
    path_task_folder = os.path.join(
        config['DATASET_FOLDER'],
        config['DATASET_PREFIX'] + str(dataset.id),
        config['TASK_PREFIX'] + str(task.id)
    )

    try:
        os.makedirs(path_task_folder)
    except OSError:
        # Raise exception only if it's something else than 'Directory already exists' error
        if not os.path.isdir(path_task_folder):
            raise

    # Save the unformatted scanpath data file (to be deleted after formatting) in the directory created above
    path_file_scanpaths = os.path.join(path_task_folder, config['SCANPATHS_FILE_RAW'])
    file_scanpaths.save(path_file_scanpaths)

    # Select the columns we wish to keep after formatting
    keep = ['ParticipantName', 'FixationIndex', 'GazeEventType', 'GazeEventDuration', 'FixationPointX (MCSpx)',
            'FixationPointY (MCSpx)', 'MediaName']

    # Format the newly created file according to selected columns and remove the original one
    format_scanpaths(keep, path_task_folder)

    # Save the unformatted AOIs file (to be deleted after formatting)
    path_file_aois = os.path.join(path_task_folder, config['AOIS_FILE_RAW'])
    file_aois.save(path_file_aois)

    # Format the newly created file and remove the original one
    format_aois(path_task_folder)

    # Create the static images folder for the new dataset task
    create_task_img_folder(dataset, task, file_bg_image)


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
        # Save the background image with name specified in the config while keeping the original extension
        config['BG_IMG_FILE']) + os.path.splitext(file_bg_image.filename)[-1]
    )


def format_scanpaths(keep_cols, path_folder):
    try:
        fr = pd.read_csv(os.path.join(path_folder, config['SCANPATHS_FILE_RAW']), sep='\t')

        # Drop the duplicate fixation values from the CSV file
        fr = fr.drop_duplicates(subset=['ParticipantName', 'FixationIndex'])

        # Keep only fixations lasting longer than X ms
        fr = fr[fr.GazeEventType != 'Unclassified']
        fr = fr[fr.GazeEventType != 'Saccade']
        fr = fr[fr.GazeEventDuration > 100]

        # Drop fixations with negative point coordinates
        fr = fr[fr['FixationPointX (MCSpx)'] > 0]
        fr = fr[fr['FixationPointY (MCSpx)'] > 0]
        # fr = fr.sort_values(['ParticipantName', 'FixationIndex'])

        # Keep only relevant columns
        fr = fr[keep_cols]

        # Save formatted data & delete raw file uploaded by the user
        fr.to_csv(os.path.join(path_folder, config['SCANPATHS_FILE']), index=False, sep='\t')
        silent_file_remove(os.path.join(path_folder, config['SCANPATHS_FILE_RAW']))
    except:
        silent_file_remove(os.path.join(path_folder, config['SCANPATHS_FILE_RAW']))
        traceback.print_exc()
        raise ValueError('Failed to parse scanpath data file')


def format_aois(path_folder):
    file_header = ['FullName', 'XFrom', 'XSize', 'YFrom', 'YSize', 'ShortName']
    sep = '\t'

    with open(os.path.join(path_folder, config['AOIS_FILE']), 'w') as fw:
        # Write table headers divided by separator (except for the last one)
        for index, column in enumerate(file_header):
            fw.write(column if index == (len(file_header) - 1) else column + sep)

        fw.write('\n')

        with open(os.path.join(path_folder, config['AOIS_FILE_RAW']), 'r') as fr:
            name_it = 0

            for line in fr:
                line_data = line.strip().split(':')

                # Handle blank lines
                if not line.strip():
                    continue
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
                        silent_file_remove(os.path.join(path_folder, config['AOIS_FILE']))
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
                        silent_file_remove(os.path.join(path_folder, config['AOIS_FILE']))
                        raise ValueError('Maximum number of AOIs (52) reached')

                    fw.write(
                        act_aoi['name'] + sep +
                        str(x_from) + sep +
                        str(x_size) + sep +
                        str(y_from) + sep +
                        str(y_size) + sep +
                        act_aoi['shortName'] + '\n')

                    # Two-character AOIs turned out to be a trouble later'
                    name_it += 1

                    # Skip last vertex (unnecessary) and move to the next AOI
                    line = next(fr)
                    line = next(fr)
                # Skip empty or unknown formatted lines
                else:
                    continue

    # Delete raw data uploaded by the user
    silent_file_remove(os.path.join(path_folder, config['AOIS_FILE_RAW']))


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
