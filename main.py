from flask import Flask, render_template
from sta import *

app = Flask(__name__)


@app.route('/')
def redirect_index():
    return index()


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run()
