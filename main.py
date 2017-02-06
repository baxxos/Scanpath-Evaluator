from flask import Flask, render_template, request
from passlib.hash import sha256_crypt
from User import User
from DatasetTask import DatasetTask
from sta import sta_run, custom_run, get_task_data_json
from database import session, exc

import json

app = Flask(__name__)
app.debug = True

# TODO consider prefixing Angular directives with 'data-ng' prefix to ensure valid HTML and reduce IDE warnings


@app.route('/')
def redirect_index():
    return render_template('index.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        json_data = json.loads(request.data)

        # Back-end password validation
        if len(json_data['password']) < 8:
            return json.dumps({
                'success': False,
                'message': 'Password too short - enter at least 8 characters.'
            })

        user = User(password=sha256_crypt.hash(json_data['password']), email=json_data['email'],
                    name=json_data['name'], surname=json_data['surname'])
    except KeyError:
        return json.dumps({
            'success': False,
            'message': 'Required user attributes are missing'
        })

    try:
        session.add(user)
        session.commit()
    except exc.IntegrityError:
        session.rollback()
        return json.dumps({
            'success': False,
            'message': 'Integrity error: e-mail address is already taken.'
        })
    except:
        session.rollback()
        return json.dumps({
            'success': False,
            'message': 'Internal database error.'
        })

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
        return json.dumps({
            'success': False,
            'message': 'Custom scanpath attribute is missing.'
        })

    # Verify the custom scanpath formatting - only letters describing AOIs
    if str(custom_scanpath).isalpha():
        task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
        task.load_data()
        return custom_run(task, custom_scanpath)
    else:
        return json.dumps({
            'success': False,
            'message': 'Wrong custom scanpath format - alpha characters only.'
        })


@app.route('/sta', methods=['POST'])
def get_trending_scanpath():
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']
    except KeyError:
        return json.dumps({
            'success': False,
            'message': 'Task ID is missing'
        })

    task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
    task.load_data()
    return sta_run(task)


@app.route('/get_task_data', methods=['POST'])
def get_task_data():
    try:
        json_data = json.loads(request.data)
        task_id = json_data['taskId']
    except KeyError:
        return json.dumps({
            'success': False,
            'message': 'Task ID is missing'
        })
    task = session.query(DatasetTask).filter(DatasetTask.id == task_id).one()
    task.load_data()
    return get_task_data_json(task)


@app.route('/get_data_tree', methods=['POST'])
def get_data_tree():
    """ Get the dataset-task tree structure available to the current user ID which is passed in as parameter """

    try:
        json_data = json.loads(request.data)
        user_id = json_data['userId']
    except KeyError:
        return json.dumps({
            'success': False,
            'message': 'User ID is missing'
        })

    user = session.query(User).filter(User.id == user_id).one()

    """
    user = User(name='admin', surname='admin', password='admin', email='admin@admin.sk')
    dataset1 = Dataset(name='template_sta', description='description')
    user.datasets.append(dataset1)
    session.add(user)
    session.commit()

    task1 = DatasetTask(url='http://ncc.metu.edu.tr/', name='my_task', description='description')
    dataset1.tasks.append(task1)

    session.add(task1)
    session.commit()

    dataset2 = Dataset(name='template_other', description='description')
    task2 = DatasetTask(url='http://ncc.metu.edu.tr/', name='other_task', description='description')
    dataset2.tasks.append(task2)
    user.datasets.append(dataset2)

    session.add(dataset2)
    session.commit()
    """

    try:
        return user.get_data_tree_json()
    except:
        return json.dumps({
            'success': False,
            'message': 'Failed to obtain data tree structure in get_data_tree_json()'
        })

if __name__ == '__main__':
    # App is threaded=true due to slow loading times on localhost
    app.run(host='127.0.0.1', port=8888, threaded=True)
