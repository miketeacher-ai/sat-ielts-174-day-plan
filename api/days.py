"""GET /api/days — day index (topic, word count)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify  # noqa: E402

from _core import study_plan  # noqa: E402

app = Flask(__name__)


@app.route('/api/days')
def handler():
    return jsonify([
        {"day": d["day"], "topic": d["topic"], "word_count": len(d["words"])}
        for d in study_plan
    ])
