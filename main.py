from flask import Flask, render_template, request
from sta import *


app = Flask(__name__)


@app.route('/')
def redirect_index():
    return render_template('index.html')


@app.route('/custom', methods=['GET', 'POST'])
def get_similarity_to_custom():
    # TODO validation also getting fixations besides scanpath itself
    json_data = json.loads(request.data)
    return custom_run(json_data["customScanpath"])


@app.route('/sta')
def get_trending_scanpath():
    return sta_run()


@app.route('/get_dataset')
def get_dataset():
    return get_dataset_json()


if __name__ == '__main__':
    app.run()
