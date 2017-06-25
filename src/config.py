import os

# Database connection
if os.environ.get('DATABASE_URL') is None:
    DB_URL = 'postgresql://postgres:postgres@localhost/scanpath-evaluator'
else:
    DB_URL = os.environ['DATABASE_URL']

# Basic app configuration
config = {
    'SQLALCHEMY_DATABASE_URI': DB_URL,
    'DATASET_FOLDER': 'datasets',
    'DATASET_PREFIX': 'dataset',
    'TASK_PREFIX': 'task',
    'BG_IMG_FILE': 'main',
    'MIN_PASSWORD_LEN': 8
}

# When restoring the database from a backup, use these credentials for the dummy (guest) user:
# username: admin@admin | pwd: adminadmin

