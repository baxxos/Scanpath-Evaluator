import json
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship

from src.database import Base, db_session
from src.models.Dataset import Dataset
from src.models.DatasetTask import DatasetTask


class User(Base):
    """ Class mirroring application users """

    # Name of corresponding schema table
    __tablename__ = 'users'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    date_created = Column(Date, default=datetime.now())

    # Reference to the datasets owned by current user
    datasets = relationship('Dataset', backref='user', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return "<User(name='%s', surname='%s', email='%s', password='%s')>" % (
            self.name, self.surname, self.email, self.password)

    def get_data_tree_json(self):
        # Load datasets owned by current user
        my_datasets = db_session.query(Dataset).filter(Dataset.user_id == self.id)
        data_tree = []

        for dataset in my_datasets:
            data_tree.append({
                'label': dataset.name,
                'id': dataset.id,
                'children': []
            })

            # Load tasks owned by current dataset
            my_tasks = db_session.query(DatasetTask).filter(DatasetTask.dataset_id == dataset.id)

            for task in my_tasks:
                data_tree[len(data_tree) - 1]['children'].append({
                    'label': task.name,
                    'id': task.id
                })

        return json.dumps(data_tree)
