from pathlib import Path
import sys
import os

import flask
import logging


root = Path(__file__).parent.parent.resolve()

sys.path.append(root.as_posix())
from utils.misc import render_index

app = flask.Flask(__name__, template_folder= root / "templates")
logger = logging.getLogger(__file__)
logger.setLevel("INFO")


@app.route("/")
@app.route("/index")
def index():
    print("accessed index via", flask.request.path)
    css_path = Path(__file__).parent.resolve() / "index.css"
    return render_index(css_path)

@app.route("/set_lights", methods=["POST"])
def set_lights():
    request_data = flask.request.get_json() or {}
    print(request_data)
    return "OK"
    

app.run()