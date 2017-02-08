from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Dataset(Base):
    """ Class which groups several dataset tasks into a custom themed dataset """

    # Name of corresponding schema table
    __tablename__ = 'datasets'

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date_created = Column(Date, default=datetime.now())
    date_updated = Column(Date, onupdate=datetime.now())

    # Reference to the dataset tasks owned by this dataset
    tasks = relationship('DatasetTask', backref='dataset', cascade='all, delete-orphan', passive_deletes=True)

