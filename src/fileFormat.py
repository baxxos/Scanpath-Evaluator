from config import config
from os import path
import pandas as pd
import traceback
import string


# TODO arguments filepath and filename
def extract_cols(keep_cols, file_path):
    try:
        fr = pd.read_csv(file_path, sep='\t')

        # Filter the relevant rows from the CSV file
        fr = fr[fr.GazeEventType != 'Unclassified']
        fr = fr[fr.GazeEventType != 'Saccade']
        fr = fr[fr.GazeEventDuration > 100]
        fr = fr[fr['GazePointX (MCSpx)'] > 0]

        # Filter the relevant columns from the CSV file
        fw = fr[keep_cols]

        fw.to_csv('D:\\FIIT\\Ostatne\\BP\\DOD2016_Dataset\\Scanpaths.txt', index=False, sep='\t')
    except Exception as e:
        traceback.print_exc()


def format_aois(filepath, filename):
    file_header = ['FullName', 'XFrom', 'XSize', 'YFrom', 'YSize', 'ShortName']
    sep = '\t'

    with open(path.join(filepath, filename + '_formatted.txt'), 'w') as fw:
        # Write table headers divided by separator (except for the last one)
        for index, column in enumerate(file_header):
            fw.write((column + sep).rstrip() if index == (len(file_header) - 1) else column + sep)
        fw.write('\n')

        with open(path.join(filepath, filename + '.txt'), 'r') as fr:

            my_iter = 0

            for line in fr:
                if my_iter > len(string.uppercase) - 1:
                    break

                # AOI full name
                fw.write((line.split(':')[1]).strip() + sep)

                # TODO handle aois without 4 vertices
                # TODO remove blank lines on load

                # Skip irrelevant data
                for i in xrange(10):
                    line = next(fr)

                # Handle vertices and compute their lengths
                coords_from = line.split('\t')

                # '222,55' -> 222.55 -> 222
                x_from = int(float(coords_from[0].replace(',', '.')))
                y_from = int(float(coords_from[1].replace(',', '.')))

                # Normalize negative values
                x_from = x_from if x_from > 0 else 0
                y_from = y_from if y_from > 0 else 0

                line = next(fr)
                x_size = int(float(line.split('\t')[0].replace(',', '.'))) - x_from

                line = next(fr)
                y_size = int(float(line.split('\t')[1].replace(',', '.'))) - y_from

                fw.write(
                    str(x_from) + sep +
                    str(x_size) + sep +
                    str(y_from) + sep +
                    str(y_size) + sep +
                    string.uppercase[my_iter] + '\n')

                for i in xrange(3):
                    line = next(fr)

                my_iter += 1


# keep = ['RecordingDate', 'StudioProjectName', 'StudioTestName', 'ParticipantName', 'MediaName', 'GazeEventType',
#        'GazeEventDuration', 'GazePointX (MCSpx)', 'GazePointY (MCSpx)']

keep = ['ParticipantName', 'GazeEventDuration', 'GazeEventDuration', 'GazeEventDuration', 'GazePointX (MCSpx)',
        'GazePointY (MCSpx)', 'MediaName']

extract_cols(keep, 'D:\\FIIT\\Ostatne\\BP\\DOD2016_Dataset\\DOD2016.txt')
# format_aois('D:\\FIIT\\Ostatne\\BP\\DOD2016_Dataset', 'aois')
