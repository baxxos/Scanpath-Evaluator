from flask import Flask, render_template, request
from User import User
from DatasetTask import DatasetTask
from sta import sta_run, custom_run, get_task_data_json
from database import session
from config import config
from sqlalchemy import exc, orm
from passlib.hash import sha256_crypt

import json

app = Flask(__name__)
app.debug = True


# TODO consider prefixing Angular directives with 'data-ng' prefix to ensure valid HTML and reduce IDE warnings
def handle_error(message):
    return json.dumps({
        'success': False,
        'message': message
    })


def handle_success(load):
    return json.dumps({
        'success': True,
        'load': json.dumps(load)
    })


@app.route('/')
def redirect_index():
    return render_template('index.html')


@app.route('/api/auth',  methods=['POST'])
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
            return handle_success({})
        else:
            return handle_error('Invalid user credentials - try again.')
    except orm.exc.NoResultFound:
        return handle_error('Invalid user credentials - try again.')
    except Exception as e:
        print e.message
        return handle_error('Internal database error - try again later.')


# TODO move to separate api.py file
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        json_data = json.loads(request.data)

        # Back-end password validation
        if len(json_data['password']) < config['MIN_PASSWORD_LEN']:
            return handle_error('Password too short - enter at least 8 characters.')

        user = User(password=sha256_crypt.hash(json_data['password']), email=json_data['email'],
                    name=json_data['name'], surname=json_data['surname'])
    except KeyError:
        return handle_error('Required user attributes are missing')

    try:
        session.add(user)
        session.commit()
    except exc.IntegrityError:
        session.rollback()
        return handle_error('Integrity error: e-mail address is already taken.')
    except:
        session.rollback()
        return handle_error('Internal database error.')

    return json.dumps({
        'success': True
    })


@app.route('/custom', methods=['GET', 'POST'])
def get_similarity_to_custom():
    # TODO consider fixations length [A, B] -> fixation == 50ms, [AAABB] = [A(150), B(100)]
    # Check if the request data contains the custom scanpath
    try:
        json_data = json.loads(request.data)
        custom_scanpath = json_data['customScanpath']
        task_id = json_data['taskId']
    except KeyError:
        return handle_error('Custom scanpath attribute is missing.')

    # Verify the custom scanpath formatting - only letters describing AOIs
    if str(custom_scanpath).isalpha():
        task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()
        return custom_run(task, custom_scanpath)
    else:
        return handle_error('Wrong custom scanpath format - alpha characters only.')


@app.route('/sta', methods=['POST'])
# TODO GET method
def get_trending_scanpath():
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']
    except KeyError:
        return handle_error('Task ID is missing')

    task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
    task.load_data()

    return sta_run(task)


@app.route('/get_task_data', methods=['POST'])
# TODO GET method
def get_task_data():
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']
    except KeyError:
        return handle_error('Task ID is missing')

    task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
    task.load_data()
    return get_task_data_json(task)


@app.route('/get_data_tree', methods=['POST'])
# TODO GET method
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
