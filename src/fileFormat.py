from config import config
import pandas as pd
import os
import traceback
import string
import shutil


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


def create_task_folder(dataset, task, file_regions, file_scanpaths):
    os.makedirs(os.path.join(
        config['DATASET_FOLDER'],
        config['DATASET_PREFIX'] + str(dataset.id),
        config['TASK_PREFIX'] + str(task.id))
    )

    # Save the unformatted scanpath data file (to be deleted after formatting) in the directory created above
    path_file_scanpaths = os.path.join(
        config['DATASET_FOLDER'],
        config['DATASET_PREFIX'] + str(dataset.id),
        config['TASK_PREFIX'] + str(task.id)
    )

    file_scanpaths.save(os.path.join(
        path_file_scanpaths,
        config['SCANPATHS_FILE_RAW'])
    )

    # Format the newly created file and remove the original one
    keep = ['ParticipantName', 'FixationIndex', 'GazeEventDuration', 'GazeEventDuration', 'FixationPointX (MCSpx)',
            'FixationPointY (MCSpx)', 'MediaName']
    format_scanpaths(keep, path_file_scanpaths)

    # Save the unformatted AOIs file (to be deleted after formatting)
    path_file_regions = os.path.join(
        config['DATASET_FOLDER'],
        config['DATASET_PREFIX'] + str(dataset.id),
        config['TASK_PREFIX'] + str(task.id)
    )

    file_regions.save(os.path.join(
        path_file_regions,
        config['AOIS_FILE_RAW'])
    )

    # Format the newly created file and remove the original one
    format_aois(path_file_regions)


def format_scanpaths(keep_cols, file_path):
    try:
        fr = pd.read_csv(os.path.join(file_path, config['SCANPATHS_FILE_RAW']), sep='\t')

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
        fr.to_csv(os.path.join(file_path, config['SCANPATHS_FILE']), index=False, sep='\t')
        silent_file_remove(os.path.join(file_path, config['SCANPATHS_FILE_RAW']))
    except:
        silent_file_remove(os.path.join(file_path, config['SCANPATHS_FILE_RAW']))
        traceback.print_exc()
        raise ValueError('Failed to parse scanpath data file')


def format_aois(file_path):
    file_header = ['FullName', 'XFrom', 'XSize', 'YFrom', 'YSize', 'ShortName']
    sep = '\t'

    with open(os.path.join(file_path, config['AOIS_FILE']), 'w') as fw:
        # Write table headers divided by separator (except for the last one)
        for index, column in enumerate(file_header):
            fw.write(column if index == (len(file_header) - 1) else column + sep)

        fw.write('\n')

        with open(os.path.join(file_path, config['AOIS_FILE_RAW']), 'r') as fr:
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
                        silent_file_remove(os.path.join(file_path, config['AOIS_FILE']))
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
                        silent_file_remove(os.path.join(file_path, config['AOIS_FILE']))
                        raise ValueError('Maximum number of AOIs (52) reached')

                    fw.write(
                        act_aoi['name'] + sep +
                        str(x_from) + sep +
                        str(x_size) + sep +
                        str(y_from) + sep +
                        str(y_size) + sep +
                        act_aoi['shortName'] + '\n')

                    # Two-character AOIs turned out to be a trouble later
                    # string.uppercase[name_it % len(string.uppercase)] +
                    # string.lowercase[name_it / len(string.lowercase)] + '\n'
                    name_it += 1

                    # Skip last vertex (unnecessary) and move to the next AOI
                    line = next(fr)
                    line = next(fr)
                # Skip empty or unknown formatted lines
                else:
                    continue

    # Delete raw data uploaded by the user
    silent_file_remove(os.path.join(file_path, config['AOIS_FILE_RAW']))
