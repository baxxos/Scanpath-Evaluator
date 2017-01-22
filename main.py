from flask import Flask, render_template, request
from sta import sta_run, custom_run, get_dataset_json
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


@app.route('/get_dataset')
def get_dataset():
    return get_dataset_json()


if __name__ == '__main__':
    app.run()
