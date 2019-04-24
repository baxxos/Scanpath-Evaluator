import math
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship

from database import Base


class Dataset(Base):
    """ Class which groups several dataset tasks into a custom themed dataset """

    # Name of corresponding schema table
    __tablename__ = 'datasets'
    __table_args__ = {'keep_existing': True}

    # Table columns
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date_created = Column(DateTime, default=datetime.now())
    date_updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    # Recording environment attributes
    screen_res_x = Column(Integer)
    screen_res_y = Column(Integer)
    screen_size = Column(Numeric)
    accuracy_degree = Column(Numeric)
    tracker_distance = Column(Numeric)

    # Reference to the dataset tasks owned by this dataset
    tasks = relationship('DatasetTask', backref='dataset', cascade='all, delete-orphan', passive_deletes=True)

    def get_ppi(self):
        # Pythagorean theorem
        diagonal_res = math.sqrt(pow(int(self.screen_res_x), 2) + pow(int(self.screen_res_y), 2))
        ppi = diagonal_res / float(self.screen_size)

        return ppi

    def get_error_rate_area(self):
        # Calculate error rate area (in cm by default)
        error_rate_area_cm = math.tan(math.radians(float(self.accuracy_degree))) * float(self.tracker_distance)
        error_rate_area_pixels = (error_rate_area_cm * self.get_ppi()) / 2.54

        return round(error_rate_area_pixels, 2)

    def to_json(self):
        tasks_json = []

        # Convert all children tasks into JSON format
        for task in self.tasks:
            tasks_json.append(task.to_json())

        # Recording environment data in a separate object
        rec_environment = {
            'screenResX': self.screen_res_x,
            'screenResY': self.screen_res_y,
            # Decimal type is not a valid JSON value - convert to float (if defined)
            'screenSize': float(self.screen_size) if self.screen_size else None,
            'accDegree': float(self.accuracy_degree) if self.accuracy_degree else None,
            'trackerDistance': float(self.tracker_distance) if self.tracker_distance else None
        }

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dateCreated': str(self.date_created),
            'dateUpdated': str(self.date_updated),
            # 'recEnvironment': rec_environment,
            'tasks': tasks_json
        }

