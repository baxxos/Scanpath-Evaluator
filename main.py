from flask import Flask
from sta import *

app = Flask(__name__)


@app.route('/')
def hello_world():
    return str(sta_run());


if __name__ == '__main__':
    app.run()
