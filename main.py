import json
import os
import traceback

from datetime import timedelta, datetime
from flask import Flask, render_template, request, session
from passlib.hash import sha256_crypt
from sqlalchemy import exc, orm

import src.fileFormat as fileFormat
import src.scanpathUtils as spUtil
from src.config import config
from src.database import db_session
from src.models.Dataset import Dataset
from src.models.DatasetTask import DatasetTask
from src.models.User import User
from src.scanpathAlgs import sta, emine, dotplot

# App configuration
app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')
app.debug = True

# For mocking sessions etc.
dev_mode = True


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=12)


def is_user_logged_in():
    return dev_mode or ('user' in session)


def is_user_authorized(user_id):
    return dev_mode or (is_user_logged_in() and (session['user'] == user_id))


# Response methods
def handle_error(message='Internal database error - try again later.'):
    return json.dumps({
        'success': False,
        'message': message
    })


def handle_success(load=None):
    return json.dumps({
        'success': True,
        'load': load if load is not None else ''
    })


def handle_unauthorized():
    return handle_error('Unauthorized access')


# Routing methods
@app.route('/')
def redirect_index():
    return render_template('index.html')


@app.route('/api/user/auth',  methods=['POST'])
def authenticate():
    # Process the request - verify required info
    try:
        json_data = json.loads(request.data)
        email = json_data['email']
        password = json_data['password']
    except KeyError:
        return handle_error('Failed to login - user auth data invalid.')

    # Query the database for an user matching the info from the request
    try:
        user = db_session.query(User).filter(User.email == email).one()

        if sha256_crypt.verify(password, user.password):
            session['user'] = user.id

            return handle_success({
                'id': user.id
            })
        else:
            return handle_error('Invalid user credentials - try again.')
    except orm.exc.NoResultFound:
        return handle_error('Invalid user credentials - try again.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/user/logout', methods=['POST'])
def logout_user():
    # Drop the current session and notify the user
    session.pop('user', None)
    session.clear()
    return handle_success()


@app.route('/api/user/add', methods=['POST'])
def add_user():
    try:
        json_data = json.loads(request.data)

        # Back-end password validation
        if len(json_data['password']) < config['MIN_PASSWORD_LEN']:
            return handle_error('Password too short - enter at least ' + config['MIN_PASSWORD_LEN'] + ' characters.')

        user = User(password=sha256_crypt.hash(json_data['password']), email=json_data['email'],
                    name=json_data['name'], surname=json_data['surname'])
    except KeyError:
        return handle_error('Required user attributes are missing')

    try:
        # Commit DB changes
        db_session.add(user)
        db_session.commit()

        return handle_success()
    except exc.IntegrityError:
        db_session.rollback()
        return handle_error('Integrity error: e-mail address is already taken.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/user/get_data_tree', methods=['GET'])
def get_data_tree():
    """ Get the dataset-task tree structure available to the current user ID which is passed in as parameter """

    try:
        user_id = request.args.get('userId', type=int)

        if not is_user_authorized(user_id):
            return handle_unauthorized()

        user = db_session.query(User).filter(User.id == user_id).one()
    except orm.exc.NoResultFound:
        return handle_error('Unknown user ID')

    try:
        return user.get_data_tree_json()
    except:
        traceback.print_exc()
        return handle_error('Failed to obtain user data tree structure')


@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    if not is_user_logged_in():
        return handle_unauthorized()

    try:
        dataset_id = request.args.get('datasetId', type=int)
        dataset = db_session.query(Dataset).filter(Dataset.id == dataset_id).one()

        if not is_user_authorized(dataset.user_id):
            return handle_unauthorized()
        else:
            return handle_success(dataset.to_json())
    except orm.exc.NoResultFound:
        return handle_error('Invalid dataset ID.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/dataset', methods=['POST'])
def add_dataset():
    """ Creates a new dataset instance owned by the currently logged in user """

    try:
        json_data = json.loads(request.data)
        user_id = json_data['userId']

        # Check authorization & validate attribute values
        if not is_user_authorized(user_id):
            return handle_unauthorized()
        elif len(json_data['name']) == 0:
            raise KeyError

        dataset = Dataset(
            name=json_data['name'], description=json_data['description'], user_id=user_id,
            accuracy_degree=json_data['recEnvironment'].get('accDegree'),
            screen_size=json_data['recEnvironment'].get('screenSize'),
            screen_res_x=json_data['recEnvironment'].get('screenResX'),
            screen_res_y=json_data['recEnvironment'].get('screenResY'),
            tracker_distance=json_data['recEnvironment'].get('trackerDistance')
        )

        # Commit DB changes
        db_session.add(dataset)
        db_session.commit()

        # Reflect the changes on the server side - create a new folder named after dataset PK
        os.makedirs(os.path.join(config['DATASET_FOLDER'], config['DATASET_PREFIX'] + str(dataset.id)))

        return handle_success({
            'id': dataset.id
        })
    except KeyError:
        return handle_error('Required attributes are missing')
    except OSError:
        return handle_error('Error while creating backend dataset hierarchy')
    except orm.exc.NoResultFound:
        return handle_error('Invalid user credentials - try logging in again.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/dataset', methods=['PUT'])
def edit_dataset():
    """ Updates an existing dataset instance, if owned by the currently logged in user """

    try:
        json_data = json.loads(request.data)
        dataset = db_session.query(Dataset).filter(Dataset.id == json_data['id']).one()

        # Check authorization & validate attribute values
        if not is_user_authorized(dataset.user_id):
            return handle_unauthorized()
        elif len(json_data['name']) == 0:
            raise KeyError

        # Update all attributes of the mapped object
        dataset.name = json_data['name']
        dataset.date_updated = datetime.now()
        dataset.description = json_data['description']
        dataset.accuracy_degree = json_data['recEnvironment'].get('accDegree')
        dataset.screen_size = json_data['recEnvironment'].get('screenSize')
        dataset.screen_res_x = json_data['recEnvironment'].get('screenResX')
        dataset.screen_res_y = json_data['recEnvironment'].get('screenResY')
        dataset.tracker_distance = json_data['recEnvironment'].get('trackerDistance')

        # Commit DB changes
        db_session.commit()

        return handle_success()
    except KeyError:
        return handle_error('Required attributes are missing')
    except orm.exc.NoResultFound:
        return handle_error('Invalid user credentials - try logging in again.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/dataset', methods=['DELETE'])
def del_dataset():
    """ Deletes an existing dataset instance, if owned by the currently logged in user"""

    try:
        json_data = json.loads(request.data)

        dataset_id = json_data['datasetId']
        dataset = db_session.query(Dataset).filter(Dataset.id == dataset_id).one()

        # Only proceed, if the dataset to be removed belongs to the request owner
        if not is_user_authorized(dataset.user_id):
            return handle_unauthorized()

        # Remove the dataset visuals from static folder
        fileFormat.silent_dir_remove(os.path.join(
            'static', 'images', 'datasets',
            config['DATASET_PREFIX'] + str(dataset_id)),
        )

        # Commit changes to the DB
        for task in dataset.tasks:
            db_session.delete(task)

        db_session.delete(dataset)
        db_session.commit()

        return handle_success()
    except KeyError:
        return handle_error('Required attributes are missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect dataset ID')
    except:
        return handle_error()


@app.route('/api/task', methods=['GET'])
def get_dataset_task():
    """ Returns JSON formatted task data (individual scanpaths, visuals, similarities etc.) """

    if not is_user_logged_in():
        return handle_unauthorized()

    # Load request arguments and return task info
    try:
        task_id = request.args.get('taskId', type=int)

        task = db_session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()

        # Check if the task belongs to a dataset owned by the user ID specified in the GET request
        if not is_user_authorized(task.dataset.user_id):
            return handle_unauthorized()
        else:
            # Return data formatted as expected by the frontend
            return handle_success({
                'name': task.name,
                'scanpaths': task.scanpath_data_formatted,
                'visuals': task.visuals,
                'aois': task.aoi_data
            })
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/task', methods=['POST'])
def add_dataset_task():
    if not is_user_logged_in():
        return handle_unauthorized()

    try:
        # Parse the non-file form data (user inputs)
        json_data = request.form.to_dict()

        # Multipart forms don't support nested objects - therefore the retarded key names
        file_scanpaths = request.files['files[fileScanpaths]']
        file_regions = request.files['files[fileRegions]']
        file_bg_image = request.files['files[fileBgImage]']

        # Find parent dataset and verify its owner
        dataset = db_session.query(Dataset).filter(Dataset.id == int(json_data['datasetId'])).one()

        # Check authorization & validate attribute values
        if not is_user_authorized(dataset.user_id):
            return handle_unauthorized()
        elif len(json_data['name']) == 0:
            raise KeyError

        keep_cols = ['ParticipantName', 'FixationIndex', 'GazeEventType', 'GazeEventDuration',
                     'FixationPointX (MCSpx)', 'FixationPointY (MCSpx)']

        # Create a new empty task instance
        task = DatasetTask(name=json_data['name'],
                           url=json_data['url'] if 'url' in json_data else None,
                           description=json_data['description'],
                           dataset_id=dataset.id)

        # Get relevant data from the input file
        task.scanpath_data_raw = fileFormat.process_scanpaths(file_scanpaths, keep_cols, 100, task.url)

        # Additional data to be saved in the DB along with the previously processed raw scanpath data
        task.aoi_data = fileFormat.process_aois(file_regions)
        task.scanpath_data_formatted = spUtil.get_formatted_sequences(task)

        # Commit DB changes
        dataset.tasks.append(task)
        db_session.commit()

        # Create a folder for this task's static images
        fileFormat.create_task_img_folder(dataset, task, file_bg_image)

        return handle_success({
            'id': task.id
        })
    except KeyError:
        traceback.print_exc()
        return handle_error('Required attributes are missing')
    except orm.exc.NoResultFound:
        return handle_error('Parent dataset ID not found - create one first')
    except ValueError:
        traceback.print_exc()
        return handle_error('Failed to parse the submitted data format.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/task', methods=['PUT'])
def edit_task():
    """ Updates an existing dataset instance, if owned by the currently logged in user """

    try:
        json_data = json.loads(request.data)
        task = db_session.query(DatasetTask).filter(DatasetTask.id == json_data['id']).one()

        # Check authorization & validate attribute values
        if not is_user_authorized(task.dataset.user_id):
            return handle_unauthorized()
        elif len(json_data['name']) == 0:
            raise KeyError

        # Update all attributes of the mapped object
        task.name = json_data['name']
        task.date_updated = datetime.now()
        task.description = json_data['description']

        # Commit DB changes
        db_session.commit()

        return handle_success()
    except KeyError:
        return handle_error('Required attributes are missing')
    except orm.exc.NoResultFound:
        return handle_error('Invalid user credentials - try logging in again.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/task', methods=['DELETE'])
def del_dataset_task():
    if not is_user_logged_in():
        return handle_unauthorized()

    try:
        json_data = json.loads(request.data)
        task = db_session.query(DatasetTask).filter(DatasetTask.id == json_data['taskId']).one()

        if not is_user_authorized(task.dataset.user_id):
            return handle_unauthorized()

        # Remove the dataset visuals from static folder
        fileFormat.silent_dir_remove(os.path.join(
            'static', 'images', 'datasets',
            config['DATASET_PREFIX'] + str(task.dataset_id),
            config['TASK_PREFIX'] + str(task.id))
        )

        # Commit changes to the DB
        db_session.delete(task)
        db_session.commit()

        return handle_success()
    except KeyError:
        return handle_error('Task attributes are missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        return handle_error()


@app.route('/api/scanpath/custom', methods=['POST'])
def get_similarity_to_custom():
    # TODO consider fixations length [A, B] -> fixation == 50ms, [AAABB] = [A(150), B(100)]
    if not is_user_logged_in():
        return handle_unauthorized()

    # Check if the request data contains the custom scanpath
    try:
        json_data = json.loads(request.data)
        custom_scanpath = json_data['customScanpath']
        task_id = json_data['taskId']

        # Verify the custom scanpath formatting - only letters describing AOIs
        if str(custom_scanpath).isalpha():
            task = db_session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
            task.load_data()
            task.exclude_participants(json_data['excludedScanpaths'])

            return handle_success(spUtil.run_custom(task, custom_scanpath))
        else:
            return handle_error('Wrong custom scanpath format - alphabet characters only.')
    except KeyError:
        return handle_error('Custom scanpath attributes are missing.')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/scanpath/sta', methods=['POST'])
def get_sta_common():
    if not is_user_logged_in():
        return handle_unauthorized()

    # Look for the task identifier in request URL
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']

        # Load additional required data and perform run_sta
        task = db_session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()
        task.exclude_participants(json_data['excludedScanpaths'])

        return handle_success(sta.run_sta(task))
    except KeyError:
        return handle_error('Task ID is missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/scanpath/emine', methods=['POST'])
def get_emine_common():
    if not is_user_logged_in():
        return handle_unauthorized()

    # Look for the task identifier in request URL
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']

        # Load additional required data and perform run_sta
        task = db_session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()
        task.exclude_participants(json_data['excludedScanpaths'])

        return handle_success(emine.run_emine(task))
    except KeyError:
        return handle_error('Task ID is missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/scanpath/dotplot', methods=['POST'])
def get_dotplot_common():
    if not is_user_logged_in():
        return handle_unauthorized()

    # Look for the task identifier in request URL
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']

        # Load additional required data and perform run_sta
        task = db_session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()
        task.exclude_participants(json_data['excludedScanpaths'])

        return handle_success(dotplot.run_dotplot(task))
    except KeyError:
        return handle_error('Task ID is missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/scanpath/alg-compare', methods=['POST'])
def get_alg_comparison():
    if not is_user_logged_in():
        return handle_unauthorized()

    # Look for the task identifier in request URL
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']

        # Load additional required data and perform run_sta
        task = db_session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()

        # Check for any excluded algorithms and push the rest into the results array
        return handle_success([
            sta.run_sta(task) if 'sta' not in json_data['excludedAlgs'] else spUtil.run_empty('sta'),
            dotplot.run_dotplot(task) if 'dotplot' not in json_data['excludedAlgs'] else spUtil.run_empty('dotplot'),
            emine.run_emine(task) if 'emine' not in json_data['excludedAlgs'] else spUtil.run_empty('emine')
        ])
    except KeyError:
        return handle_error('Task ID is missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


if __name__ == '__main__':
    # App is threaded=true due to slow loading times on localhost
    app.run(host='localhost', port=8888, threaded=True)
