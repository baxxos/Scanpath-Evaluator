from config import config
from os import path, remove
import pandas as pd
import traceback
import string


def silent_remove(file_full_path):
    try:
        remove(file_full_path)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        print 'Failed to clean up after unsuccessful data parsing'
        traceback.print_exc()


def format_scanpaths(keep_cols, file_path):
    try:
        fr = pd.read_csv(path.join(file_path, config['SCANPATHS_FILE_RAW']), sep='\t')

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

        fr.to_csv(path.join(file_path, config['SCANPATHS_FILE']), index=False, sep='\t')
    except:
        silent_remove(path.join(file_path, config['SCANPATHS_FILE']))
        traceback.print_exc()


def format_aois(file_path):
    file_header = ['FullName', 'XFrom', 'XSize', 'YFrom', 'YSize', 'ShortName']
    sep = '\t'

    with open(path.join(file_path, config['AOIS_FILE']), 'w') as fw:
        # Write table headers divided by separator (except for the last one)
        for index, column in enumerate(file_header):
            fw.write(column if index == (len(file_header) - 1) else column + sep)

        fw.write('\n')

        # TODO split into separate methods and throw exceptions instead of return
        with open(path.join(file_path, config['AOIS_FILE_RAW']), 'r') as fr:
            name_it = 0

            try:
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
                            print 'All areas of interest must have exactly 4 vertices'
                            return
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

                        # Normalize negative values
                        x_from = x_from if x_from > 0 else 0
                        y_from = y_from if y_from > 0 else 0

                        line = next(fr)
                        x_size = int(float(line.split()[0].replace(',', '.'))) - x_from
                        x_size = abs(x_size)

                        line = next(fr)
                        y_size = int(float(line.split()[1].replace(',', '.'))) - y_from
                        y_size = abs(y_size)

                        if name_it < len(string.uppercase):
                            act_aoi['shortName'] = string.uppercase[name_it]
                        elif name_it < (len(string.uppercase) + len(string.lowercase)):
                            act_aoi['shortName'] = string.lowercase[name_it - len(string.lowercase)]
                        else:
                            print 'Maximum number of AOIs (52) reached'
                            return

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
            # Delete the incomplete file on any exception
            except:
                print 'Unexpected file format'
                silent_remove(path.join(file_path, config['AOIS_FILE']))
                traceback.print_exc()


# keep = ['ParticipantName', 'FixationIndex', 'GazeEventDuration', 'GazeEventDuration', 'FixationPointX (MCSpx)', 'FixationPointY (MCSpx)', 'MediaName']

# format_scanpaths(keep, 'D:\\FIIT\\Ostatne\\BP\\DOD2016_Dataset', 'Scanpaths', '.txt')
# format_aois('D:\\FIIT\\Ostatne\\BP\\DOD2016_Dataset', 'aois', '.txt')
