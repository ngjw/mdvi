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
    CONTENT = ""

    @classmethod
    def update(cls, raw):
        with cls.COND:
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
                'title': 'mdvi',
            }
            yield process(payload)

            cls.wait()

@app.route('/stream')
def serve():
    return flask.Response(Previewer.stream(), mimetype='text/event-stream')

@app.route('/update', methods=['POST'])
def update():
    content = flask.request.data.decode()
    Previewer.update(content)
    return 'ok'

@app.route('/')
def index():
    return flask.send_from_directory(STATIC_FOLDER, 'index.html')

def run(port, debug=False):

    if not debug:
        sys.stdout = sys.stderr = open(os.devnull, 'w')

    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    run(5000, debug=True)
