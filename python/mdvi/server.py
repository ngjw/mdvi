import json
import os
import sys
from pathlib import Path
from threading import Condition

import flask
import markdown
import mdx_math

CWD = Path(__file__).parent

app = flask.Flask(
    "mdvi",
    static_url_path="/static",
    static_folder=(STATIC_FOLDER := CWD / "web/static"),
)


class Previewer:

    COND = Condition()
    CONTENT = ""

    @classmethod
    def update(cls, raw):
        with cls.COND:
            cls.CONTENT = cls.markdown(raw)
            cls.COND.notify_all()

    @classmethod
    def markdown(cls, raw):
        extensions = [
            "fenced_code",
            mdx_math.MathExtension(use_gitlab_delimiters=True),
        ]
        return markdown.markdown(raw, extensions=extensions)

    @classmethod
    def wait(cls):

        with cls.COND:
            cls.COND.wait()

    @classmethod
    def stream(cls):

        process = lambda x: f"data: {json.dumps(x)}\n\n"

        while True:

            payload = {
                "status": "update",
                "content": cls.CONTENT,
                "title": "mdvi",
            }
            yield process(payload)

            cls.wait()


@app.route("/stream")
def serve():
    return flask.Response(Previewer.stream(), mimetype="text/event-stream")


@app.route("/update", methods=["POST"])
def update():
    content = flask.request.data.decode()
    Previewer.update(content)
    return "ok"


@app.route("/")
def index():
    return flask.send_from_directory(STATIC_FOLDER, "index.html")


def run(port, debug=False) -> None:

    if not debug:
        sys.stdout = sys.stderr = open(Path.home() / ".mdvi.log", "w")

    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    run(5000, debug=True)
