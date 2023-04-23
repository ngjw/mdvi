import os
import sys
import json
import flask
import markdown
from pathlib import Path
from threading import Condition

CWD = Path(__file__).parent

app = flask.Flask(
    'mdvi',
    static_url_path = '/static',
    static_folder = (STATIC_FOLDER := CWD / 'web/static'),
)

class Previewer:

    COND = Condition()
    TARGET = "mdvi"
    CONTENT = ""

    @classmethod
    def update(cls, file):
        with cls.COND:
            cls.TARGET = file
            raw = open(cls.TARGET, 'r').read()
            cls.CONTENT = markdown.markdown(raw)
            cls.COND.notify_all()

    @classmethod
    def wait(cls):

        with cls.COND:
            cls.COND.wait()

    @classmethod
    def stream(cls):

        process = lambda x: f'data: {json.dumps(x)}\n\n'

        while True:

            payload = {
                'status': 'update',
                'content': cls.CONTENT,
                'title': cls.TARGET,
            }
            yield process(payload)

            cls.wait()

@app.route('/stream')
def serve():
    return flask.Response(Previewer.stream(), mimetype='text/event-stream')

@app.route('/update')
def update():
    file = flask.request.args.get('file')
    Previewer.update(file)
    return file

@app.route('/')
def index():
    return flask.send_from_directory(STATIC_FOLDER, 'index.html')

def run(port):
    sys.stdout = sys.stderr = open(os.devnull, 'w')
    app.run(host='0.0.0.0', port=port)
