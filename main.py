from flask import Flask, render_template
from sta import *

app = Flask(__name__)


@app.route('/')
def redirect_index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
