from os import listdir, path
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, orm
from database import Base, session
from Dataset import Dataset
from stringEditAlgs import convert_to_strs, calc_mutual_similarity
from config import config


class DatasetTask(Base):
    """ Common class for grouping a set of scanpaths together based on files stored on the server """

    # Name of corresponding schema table
    __tablename__ = 'tasks'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    url = Column(String)
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False)
    date_created = Column(DateTime, default=datetime.now())
    date_updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now)

    # Reference to the visuals/AOIs
    # TODO

    def __init__(self, **kwargs):
        # ORM init
        super(DatasetTask, self).__init__(**kwargs)

        # Data holding objects
        self.participants = {}
        self.aois = []
        self.visuals = {}

    @orm.reconstructor
    def __init_on_load__(self):
        # Data holding objects
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
        folder_path_scanpaths = path.join(config['DATASET_FOLDER'], config['DATASET_PREFIX'] + str(dataset.id),
                                          config['TASK_PREFIX'] + str(self.id), 'scanpaths', '')
        # Construct path to scanpath AOI data based on config file - e.g. 'datasets/d1/t1/regions/aoiFile.txt'
        file_path_aoi = path.join(config['DATASET_FOLDER'], config['DATASET_PREFIX'] + str(dataset.id),
                                  config['TASK_PREFIX'] + str(self.id), 'regions', config['AOIS_FILE'])
        # Construct path to images based on config file - e.g. 'static/images/d1/t1/'
        folder_path_visuals = path.join('static', 'images', config['DATASET_FOLDER'], dataset.name, self.name, '')

        # Fill the data holding objects
        self.load_participants(folder_path_scanpaths)
        self.load_aois(file_path_aoi)
        self.load_visuals(folder_path_visuals)

    def load_participants(self, folder_path_scanpaths):
        # Fetch all files in specified folder
        files_list = listdir(folder_path_scanpaths)

        for filename in files_list:
            if filename.endswith(config['DATA_FORMAT']):
                try:
                    fo = open(folder_path_scanpaths + filename, 'r')
                except:
                    print "Failed to open specified file: " + folder_path_scanpaths + filename
                    continue
                act_file_content = fo.read()

                act_file_lines = act_file_content.split('\n')
                act_file_data = []

                # Read the file by lines (skip the first one with description)
                for y in range(1, len(act_file_lines) - 1):
                    try:
                        # If the page name argument matches the page name specified in file
                        if act_file_lines[y].index(self.url) > 0:
                            # Read the data in columns by splitting via tab character
                            act_file_data.append(act_file_lines[y].split('\t'))
                    except:
                        print "Invalid data format - line will be skipped"
                        continue

                # Return object containing array of fixations (each fixation is also an array)
                participant_identifier = filename.split(".txt")[0]
                self.participants[participant_identifier] = act_file_data

    def load_aois(self, file_path_aoi):
        try:
            fo = open(file_path_aoi, "r")
        except:
            print "Failed to open directory containing areas of interest"
            return {}

        aoi_file = fo.read()
        file_lines = aoi_file.split('\n')

        # Read the file by lines and remember Identifier, X-from, X-length, Y-from, Y-length, ShortID
        for x in range(0, len(file_lines)):
            temp = file_lines[x].split(' ')
            self.aois.append([temp[0], temp[1], temp[2], temp[3], temp[4], temp[5]])

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
                images_list[path.splitext(filename)[0]] = folder_path_visuals + filename

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

    def get_max_similarity(self, scanpaths):
        """ Function calculates most similar pair for each scanpath in the set """
        for scanpath in scanpaths:
            # Create empty max_similarity object
            max_similar = {}
            max_similar['identifier'] = ''
            max_similar['value'] = -1
            # Iterate through previously calculated similarity values of given scanpath
            for similarity_iter in scanpath['similarity']:
                similarity_val = scanpath['similarity'][similarity_iter]
                if similarity_val > max_similar['value']:
                    max_similar['value'] = similarity_val
                    max_similar['identifier'] = similarity_iter
            # Assign max_similarity object to scanpath (in JSON-style)
            scanpath['maxSimilarity'] = max_similar

    def get_min_similarity(self, scanpaths):
        """ Function calculates most similar pair for each scanpath in the set """
        for scanpath in scanpaths:
            # Create empty max_similarity object
            min_similar = {}
            min_similar['identifier'] = ''
            min_similar['value'] = 101
            # Iterate through previously calculated similarity values of given scanpath
            for similarity_iter in scanpath['similarity']:
                similarity_val = scanpath['similarity'][similarity_iter]
                if similarity_val < min_similar['value']:
                    min_similar['value'] = similarity_val
                    min_similar['identifier'] = similarity_iter
            # Assign max_similarity object to scanpath (in JSON-style)
            scanpath['minSimilarity'] = min_similar

    def get_edit_distances(self, scanpaths):
        # Store scanpaths as an array of string-converted original scanpaths
        scanpath_strs = convert_to_strs(scanpaths)

        # Calculate the edit distances
        # The order of records in scanpaths and scanpath_strs must be the same!
        calc_mutual_similarity(scanpath_strs)

        for i_first in range(0, len(scanpath_strs)):
            # Save the calculations to the original scanpaths object
            scanpaths[i_first]['similarity'] = scanpath_strs[i_first]['similarity']

