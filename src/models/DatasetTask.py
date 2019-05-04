from datetime import datetime
from os import listdir, path

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON

from src.config import config
from src.database import Base, db_session
from src.models.Dataset import Dataset


class DatasetTask(Base):
    """ Common class for grouping a set of scanpaths together based on files stored on the server """

    # Name of corresponding schema table
    __tablename__ = 'tasks'
    __table_args__ = {'keep_existing': True}

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    url = Column(String)
    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False)
    date_created = Column(DateTime, default=datetime.now())
    date_updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now)
    scanpath_data_raw = Column(JSON)
    scanpath_data_formatted = Column(JSON)
    aoi_data = Column(JSON)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dateCreated': str(self.date_created),
            'dateUpdated': str(self.date_updated)
        }

    def load_data(self):
        # Get parent dataset name
        dataset = db_session.query(Dataset).filter(Dataset.id == self.dataset_id).one()

        # Construct path to images based on config file - e.g. 'static/images/d1/t1/'
        folder_path_visuals = path.join('static', 'images', config['DATASET_FOLDER'], config['DATASET_PREFIX'] +
                                        str(dataset.id), config['TASK_PREFIX'] + str(self.id), '')

        # Fill the data holding objects
        self.load_visuals(folder_path_visuals)

    def exclude_participants(self, excluded):
        """ Exclude all given ids from the participants dict """
        try:
            for identifier in excluded:
                self.scanpath_data_raw.pop(identifier, None)
        except KeyError as e:
            print 'Participant ID to be excluded not found: ' + e.args[0]

    def load_visuals(self, folder_path_visuals):
        # Fetch all image files in specified folder (relying on extension atm)
        try:
            files_list = listdir(folder_path_visuals)
        except:
            folder_path_visuals = path.join('..', '..', folder_path_visuals)
            files_list = listdir(folder_path_visuals)

        images_list = {}
        valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp")

        # Verify if the file is image and add it to the collection
        for filename in files_list:
            if filename.endswith(valid_extensions):
                # images[main] = static/images/datasets/template_sta/main.png
                images_list[path.splitext(filename)[0]] = path.join(folder_path_visuals, filename).replace('\\', '/')

        self.visuals = images_list


