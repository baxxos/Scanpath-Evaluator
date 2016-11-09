from flask import Flask, render_template
from sta import sta_run

app = Flask(__name__)


@app.route('/')
def redirect_index():
    return render_template('index.html');


@app.route('/sta')
def trending_scanpath():
    return sta_run();


if __name__ == '__main__':
    app.run()
