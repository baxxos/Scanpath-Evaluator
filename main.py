from flask import Flask, render_template, make_response
from sta import *

app = Flask(__name__)


@app.route('/')
def redirect_index():
    return make_response(open('templates/index.html').read())


if __name__ == '__main__':
    app.run()
