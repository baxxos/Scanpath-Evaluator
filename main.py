from flask import Flask, render_template, request
from sta import sta_run, custom_run, get_task_data_json
from User import *
import json


app = Flask(__name__)
app.debug = True
# TODO consider prefixing Angular directives with 'data-ng' prefix to ensure valid HTML and reduce IDE warnings


@app.route('/')
def redirect_index():
    return render_template('index.html')


@app.route('/custom', methods=['GET', 'POST'])
def get_similarity_to_custom():
    # TODO consider fixations length [A, B] -> fixation == 50ms, [AAABB] = [A(150), B(100)]
    # Check if the request data contains the custom scanpath
    try:
        json_data = json.loads(request.data)
        custom_scanpath = json_data['customScanpath']
    except AttributeError:
        return {
            'error': True,
            'errorMsg': 'Custom scanpath attribute is missing'
        }

    # Verify the custom scanpath formatting - only letters describing AOIs
    if str(custom_scanpath).isalpha():
        return custom_run(custom_scanpath)
    else:
        return {
            'error': True,
            'errorMsg': 'Wrong custom scanpath format - alpha characters only'
        }


@app.route('/sta')
def get_trending_scanpath():
    return sta_run()


@app.route('/get_task_data')
def get_task_data():
    return get_task_data_json()


@app.route('/get_data_tree', methods=['POST'])
def get_data_tree():
    """ Get the dataset-task tree structure available to the current user ID which is passed in as parameter """

    try:
        json_data = json.loads(request.data)
        user_id = json_data['userId']
    except AttributeError:
        return {
            'error': True,
            'errorMsg': 'User ID is missing'
        }

    user = User(user_id)
    try:
        return user.get_data_tree_json()
    except:
        return {
            'error': True,
            'errorMsg': 'Failed to obtain data tree structure in get_data_tree_json()'
        }

if __name__ == '__main__':
    # App is threaded=true due to slow loading times on localhost
    app.run(host='127.0.0.1', port=8888, threaded=True)
