from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import config

# Shared ORM base class supporting CRUD operations
Base = declarative_base()

engine = create_engine(config['SQLALCHEMY_DATABASE_URI'], echo=True)

# Create missing tables etc:
# Import missing class into main.py and add the following line after the class declaration
Base.metadata.create_all(engine)

# Construct session manager
Session = sessionmaker(bind=engine)
session = Session()
