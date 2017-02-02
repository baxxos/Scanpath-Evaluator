from os import listdir, path
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from config import config
from database import Base, session
from Dataset import Dataset
from DatasetTask import DatasetTask

import json


class User(Base):
    """ Class mirroring application users """

    # Name of corresponding schema table
    __tablename__ = 'users'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date_created = Column(Date, default=datetime.now())

    # Reference to the datasets owned by current user
    datasets = relationship('Dataset', backref='user', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return "<User(name='%s', surname='%s', username='%s', password='%s')>" % (
            self.name, self.surname, self.username, self.password)

    def get_data_tree_json(self):
        # Load datasets owned by current user
        my_datasets = session.query(Dataset).filter(Dataset.user_id == self.id)
        data_tree = []

        for dataset in my_datasets:
            data_tree.append({
                'label': dataset.name,
                'id': dataset.id,
                'children': []
            })

            # Load tasks owned by current dataset
            my_tasks = session.query(DatasetTask).filter(DatasetTask.dataset_id == dataset.id)

            for task in my_tasks:
                data_tree[len(data_tree) - 1]['children'].append({
                    'label': task.name,
                    'id': task.id
                })

        return json.dumps(data_tree)

# Base.metadata.create_all(engine)
