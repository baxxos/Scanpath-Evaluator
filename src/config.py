# Basic app configuration
config = {
    'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:postgres@localhost/scanpath-evaluator',
    'DATASET_FOLDER': 'datasets',
    'DATASET_PREFIX': 'dataset',
    'TASK_PREFIX': 'task',
    'BG_IMG_FILE': 'main',
    'MIN_PASSWORD_LEN': 8
}

# When restoring the database from a backup, use these credentials for the dummy (guest) user:
# username: admin@admin | pwd: adminadmin

