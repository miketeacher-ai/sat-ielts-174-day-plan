"""GET /api/plan — full study plan (all days, words, exercises)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify  # noqa: E402

from _core import study_plan  # noqa: E402

app = Flask(__name__)


@app.route('/api/plan')
def handler():
    return jsonify(study_plan)
