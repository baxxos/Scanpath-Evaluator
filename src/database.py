from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import config

# Shared ORM base class supporting CRUD operations
Base = declarative_base()

engine = create_engine(config['SQLALCHEMY_DB_URI'], echo=False)

# Create missing tables etc:
# Example: import the missing class into run.py and add the following line just after the class declaration
# Base.metadata.create_all(engine)

# Construct session manager
Session = sessionmaker(bind=engine)
db_session = Session()
