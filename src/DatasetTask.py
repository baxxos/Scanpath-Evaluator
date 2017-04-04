from os import listdir, path
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, orm
from database import Base, session
from Dataset import Dataset
from stringEditAlgs import convert_to_str_array, calc_mutual_similarity
from config import config


class DatasetTask(Base):
    """ Common class for grouping a set of scanpaths together based on files stored on the server """

    # Name of corresponding schema table
    __tablename__ = 'tasks'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    url = Column(String, nullable=False)
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False)
    date_created = Column(DateTime, default=datetime.now())
    date_updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now)

    def __init__(self, **kwargs):
        # ORM init
        super(DatasetTask, self).__init__(**kwargs)

        # Data holding objects
        self.participants = {}
        self.aois = []
        self.visuals = {}

    @orm.reconstructor
    def __init_on_load__(self):
        # Data holding objects - gets fired after the init method. Not sure if still needed
        self.participants = {}
        self.aois = []
        self.visuals = {}

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date_created': str(self.date_created),
            'date_updated': str(self.date_updated)
        }

    def load_data(self):
        # Get parent dataset name
        dataset = session.query(Dataset).filter(Dataset.id == self.dataset_id).one()

        # Construct path to scanpath data based on config file - e.g. 'datasets/d1/t1/scanpaths/'
        file_path_scanpaths = path.join(config['DATASET_FOLDER'], config['DATASET_PREFIX'] + str(dataset.id),
                                        config['TASK_PREFIX'] + str(self.id), config['SCANPATHS_FILE'])

        # Construct path to scanpath AOI data based on config file - e.g. 'datasets/d1/t1/regions/aoiFile.txt'
        file_path_aoi = path.join(config['DATASET_FOLDER'], config['DATASET_PREFIX'] + str(dataset.id),
                                  config['TASK_PREFIX'] + str(self.id), config['AOIS_FILE'])

        # Construct path to images based on config file - e.g. 'static/images/d1/t1/'
        folder_path_visuals = path.join('static', 'images', config['DATASET_FOLDER'], config['DATASET_PREFIX'] +
                                        str(dataset.id), config['TASK_PREFIX'] + str(self.id), '')

        # Fill the data holding objects
        self.load_participants(file_path_scanpaths)
        self.load_aois(file_path_aoi)
        self.load_visuals(folder_path_visuals)

    def exclude_participants(self, excluded):
        """ Exclude all given ids from the participants dict """
        try:
            for identifier in excluded:
                self.participants.pop(identifier, None)
        except KeyError as e:
            print 'Participant ID to be excluded not found: ' + e.args[0]

    def load_participants(self, file_path_scanpaths):
        try:
            with open(file_path_scanpaths, 'r') as fr:
                file_data = []
                # Skip the first line of scanpath file (table header)
                next(fr)
                # Read the rest of the file by lines
                for act_line in fr:
                    try:
                        # If the page name argument matches the page name specified in file
                        if act_line.index(str(self.url)) > 0:
                            # Remove trailing newline and split the line into columns
                            act_line = act_line.rstrip()
                            line_cols = act_line.split('\t')

                            # Subtract the user identifier from the act line
                            participant_identifier = line_cols[0]

                            if participant_identifier not in self.participants:
                                self.participants[participant_identifier] = []

                            # Write the the line data into the data object (under user ID key)
                            self.participants[participant_identifier].append(line_cols[1:])

                            # Read the rest of the data in columns by splitting it by tab character
                            file_data.append(act_line.split('\t'))
                    except:
                        print "Invalid data format - line will be skipped"
                        continue
        except:
            print "Failed to open specified file: " + file_path_scanpaths

    def load_aois(self, file_path_aoi):
        try:
            fo = open(file_path_aoi, "r")
        except:
            print "Failed to open directory containing areas of interest"
            return {}

        aoi_file = fo.read()

        # Skip the first line containing table header
        file_lines = aoi_file.split('\n')[1:]

        # Read the file by lines and remember Identifier, X-from, X-length, Y-from, Y-length, ShortID
        for x in range(0, len(file_lines)):
            # Skip blank lines
            if not file_lines[x].strip():
                continue
            else:
                temp = file_lines[x].split('\t')
                self.aois.append([temp[0], int(temp[1]), int(temp[2]), int(temp[3]), int(temp[4]), temp[5]])

        fo.close()

    def load_visuals(self, folder_path_visuals):
        # Fetch all image files in specified folder (relying on extension atm)
        try:
            files_list = listdir(folder_path_visuals)
        except:
            return {}

        images_list = {}
        valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")

        # Verify if the file is image and add it to the collection
        for filename in files_list:
            if filename.endswith(valid_extensions):
                # images[main] = static/images/datasets/template_sta/main.png
                images_list[path.splitext(filename)[0]] = path.join(folder_path_visuals, filename).replace('\\', '/')

        self.visuals = images_list

    def format_sequences(self, sequences):
        """
        {'01': [[A, 150], [B, 250]], '02': ...} gets transformed into:
        [{'identifier': '01', 'fixations': [[A, 150], [B, 250]]}, {'identifier': '02' ... }]
        """
        formatted_sequences = []
        keys = sequences.keys()
        for it in range(0, len(sequences)):
            act_rec = {
                'identifier': keys[it],
                'fixations': sequences[keys[it]]
            }
            formatted_sequences.append(act_rec)

        return formatted_sequences

    def calc_max_similarity(self, scanpaths):
        """ Function calculates most similar pair for each scanpath in the set """
        for scanpath in scanpaths:
            # Create empty max_similarity object
            max_similar = {
                'identifier':  '',
                'value': -1
            }
            # Iterate through previously calculated similarity values of given scanpath
            for similarity_iter in scanpath['similarity']:
                similarity_val = scanpath['similarity'][similarity_iter]
                if similarity_val > max_similar['value']:
                    max_similar['value'] = similarity_val
                    max_similar['identifier'] = similarity_iter
            # Assign max_similarity object to scanpath (in JSON-style)
            scanpath['maxSimilarity'] = max_similar

        return scanpaths

    def calc_min_similarity(self, scanpaths):
        """ Function calculates least similar pair for each scanpath in the set """
        for scanpath in scanpaths:
            # Create empty max_similarity object
            min_similar = {
                'identifier': '',
                'value': 101
            }
            # Iterate through previously calculated similarity values of given scanpath
            for similarity_iter in scanpath['similarity']:
                similarity_val = scanpath['similarity'][similarity_iter]
                if similarity_val < min_similar['value']:
                    min_similar['value'] = similarity_val
                    min_similar['identifier'] = similarity_iter
            # Assign max_similarity object to scanpath (in JSON-style)
            scanpath['minSimilarity'] = min_similar

        return scanpaths

    def calc_edit_distances(self, scanpaths):
        # Store scanpaths as an array of string-converted original scanpaths
        scanpath_strs = convert_to_str_array(scanpaths)

        # Calculate the edit distances
        # The order of records in scanpaths and scanpath_strs must be the same!
        calc_mutual_similarity(scanpath_strs)

        for i_first in range(0, len(scanpath_strs)):
            # Save the calculations to the original scanpaths object
            scanpaths[i_first]['similarity'] = scanpath_strs[i_first]['similarity']

        return scanpaths

