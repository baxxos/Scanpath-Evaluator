import os

# Database connection
if os.environ.get('DATABASE_URL'):
    DB_URL = os.environ['DATABASE_URL']
else:
    # For local testing of the deployed application
    DB_URL = 'postgresql://postgres:postgres@localhost/scanpath-evaluator'

# Flask application secret key
if os.environ.get('FLASK_SECRET_KEY'):
    FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']
else:
    # For local testing of the deployed application
    FLASK_SECRET_KEY = 'V3RY_S3CR3T_K3Y'

# Basic application configuration
config = {
    'SQLALCHEMY_DB_URI': DB_URL,
    'FLASK_SECRET_KEY': FLASK_SECRET_KEY,
    'IMGUR_CLIENT_ID': os.environ.get('IMGUR_CLIENT_ID'),
    'IMGUR_CLIENT_SECRET': os.environ.get('IMGUR_CLIENT_SECRET'),
    'DATASET_FOLDER': 'datasets',
    'DATASET_PREFIX': 'dataset',
    'TASK_PREFIX': 'task',
    'BG_IMG_FILE': 'main',
    'MIN_PASSWORD_LEN': 8
}

# When restoring the database from a backup, use these credentials for the dummy (guest) user:
# username: admin@admin | pwd: adminadmin

