from flask import Flask, render_template, request
from User import User
from Dataset import Dataset
from DatasetTask import DatasetTask
from sta import sta_run, custom_run, get_task_data
from database import session
from config import config
from sqlalchemy import exc, orm
from passlib.hash import sha256_crypt

import os
import json
import traceback
import fileFormat

app = Flask(__name__)
app.debug = True


# TODO consider prefixing Angular directives with 'data-ng' prefix to ensure valid HTML and reduce IDE warnings
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
        return handle_error('User auth data invalid.')

    # Query the database for an user matching the info from the request
    try:
        user = session.query(User).filter(User.email == email).one()
        if sha256_crypt.verify(password, user.password):
            return handle_success()
        else:
            return handle_error('Invalid user credentials - try again.')
    except orm.exc.NoResultFound:
        return handle_error('Invalid user credentials - try again.')
    except Exception as e:
        print e.message
        return handle_error()


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
        session.add(user)
        session.commit()

        return handle_success()
    except exc.IntegrityError:
        session.rollback()
        return handle_error('Integrity error: e-mail address is already taken.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    try:
        dataset = session.query(Dataset).filter(Dataset.id == request.args.get('id')).one()
        return handle_success(dataset.to_json())
    except orm.exc.NoResultFound:
        return handle_error('Invalid dataset ID.')
    except:
        return handle_error()


@app.route('/api/dataset/add', methods=['POST'])
def add_dataset():
    try:
        json_data = json.loads(request.data)

        user = session.query(User).filter(User.email == json_data['userEmail']).one()
        dataset = Dataset(name=json_data['name'], description=json_data['description'], user_id=user.id)

        # Commit DB changes
        user.datasets.append(dataset)
        session.commit()

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
        return handle_error()


@app.route('/get_task_data', methods=['GET'])
def get_dataset_task():
    """ Returns JSON formatted task data (individual scanpaths, visuals, similarities etc.) """

    # Look for the task identifier in request URL
    try:
        task_id = request.args.get('taskId')
    except:
        traceback.print_exc()
        return handle_error('Task ID is missing')

    # Load additional required data and return task info
    try:
        task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()

        return handle_success(get_task_data(task))
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/task/add', methods=['POST'])
def add_dataset_task():
    try:
        # Handle request data
        try:
            # Parse the non-file form data (user inputs)
            json_data = request.form.to_dict()

            # Multipart forms don't support nested objects - therefore the retarded key names
            file_scanpaths = request.files['files[fileScanpaths]']
            file_regions = request.files['files[fileRegions]']

            # Find parent dataset and create new task instance
            dataset = session.query(Dataset).filter(Dataset.id == int(json_data['datasetId'])).one()
            task = DatasetTask(name=json_data['name'], url=json_data['url'], description=json_data['description'],
                               dataset_id=dataset.id)
        except KeyError:
            traceback.print_exc()
            return handle_error('Required attributes are missing')
        except orm.exc.NoResultFound:
            return handle_error('Parent dataset ID not found - please create one first')

        # Reflect the changes on the server side - commit & create a new folder named after dataset PK
        try:
            # Commit DB changes
            dataset.tasks.append(task)
            session.commit()

            fileFormat.create_task_folder(dataset, task, file_regions, file_scanpaths)

            return handle_success({
                'id': task.id
            })
        except ValueError:
            # Try to delete any data previously created
            session.delete(task)
            session.commit()

            fileFormat.silent_dir_remove(os.path.join(
                config['DATASET_FOLDER'],
                config['DATASET_PREFIX'] + str(dataset.id),
                config['TASK_PREFIX'] + str(task.id))
            )

            traceback.print_exc()
            return handle_error('Failed to parse the submitted data format.')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/task', methods=['DELETE'])
def del_dataset_task():
    try:
        json_data = json.loads(request.data)
        task = session.query(DatasetTask).filter(DatasetTask.id == json_data['taskId']).one()

        fileFormat.silent_dir_remove(os.path.join(
            config['DATASET_FOLDER'],
            config['DATASET_PREFIX'] + str(task.dataset_id),
            config['TASK_PREFIX'] + str(task.id))
        )

        # Commit changes to the DB
        session.delete(task)
        session.commit()

        return handle_success()
    except KeyError:
        return handle_error('Task attributes are missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        return handle_error()


@app.route('/custom', methods=['POST'])
def get_similarity_to_custom():
    # TODO consider fixations length [A, B] -> fixation == 50ms, [AAABB] = [A(150), B(100)]
    # Check if the request data contains the custom scanpath
    try:
        json_data = json.loads(request.data)
        custom_scanpath = json_data['customScanpath']
        task_id = json_data['taskId']

        # Verify the custom scanpath formatting - only letters describing AOIs
        if str(custom_scanpath).isalpha():
            task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
            task.load_data()
            task.exclude_participants(json_data['excludedScanpaths'])

            return handle_success(custom_run(task, custom_scanpath))
        else:
            return handle_error('Wrong custom scanpath format - alphabet characters only.')
    except KeyError:
        return handle_error('Custom scanpath attributes are missing.')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/sta', methods=['POST'])
def get_trending_scanpath():
    # Look for the task identifier in request URL
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']

        # Load additional required data and perform sta_run
        task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()
        task.exclude_participants(json_data['excludedScanpaths'])

        return sta_run(task)
    except KeyError:
        return handle_error('Task ID is missing')
    except orm.exc.NoResultFound:
        return handle_error('Incorrect task ID')
    except:
        traceback.print_exc()
        return handle_error()


@app.route('/api/user/get_data_tree', methods=['POST'])
def get_data_tree():
    """ Get the dataset-task tree structure available to the current user ID which is passed in as parameter """

    try:
        json_data = json.loads(request.data)
        user_email = json_data['email']
    except KeyError:
        return handle_error('User ID is missing')

    user = session.query(User).filter(User.email == user_email).one()

    try:
        return user.get_data_tree_json()
    except:
        return handle_error('Failed to obtain user data tree structure')

if __name__ == '__main__':
    # App is threaded=true due to slow loading times on localhost
    app.run(host='127.0.0.1', port=8888, threaded=True)
