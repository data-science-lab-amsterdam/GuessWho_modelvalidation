import flask
import os


app = flask.Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World! <img src="/images/Chi-300x300-cropped.jpg">'

@app.route('/images/<path:path>')
def serve_image(path):
    root_dir = os.getcwd()
    return flask.send_from_directory(os.path.join(root_dir, 'images'), path)

