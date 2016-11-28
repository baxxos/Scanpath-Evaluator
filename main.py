from flask import Flask, render_template
from sta import *


app = Flask(__name__)


@app.route('/')
def redirect_index():
    return render_template('index.html')


@app.route('/custom/<string:custom_scanpath>')
def get_similarity_to_custom(custom_scanpath):
    # TODO validation also getting fixations besides scanpath itself
    return custom_run(custom_scanpath)


@app.route('/sta')
def get_trending_scanpath():
    return sta_run()


@app.route('/get_scanpaths')
def get_scanpaths():
    return get_scanpaths_json()


if __name__ == '__main__':
    app.run()
