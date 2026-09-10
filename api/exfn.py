"""GET /api/exercise/<n> via rewrite /api/exercise/:day -> /api/exfn?day=:day."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request  # noqa: E402

from _core import study_plan  # noqa: E402

app = Flask(__name__)


@app.route('/api/exfn')
def handler():
    day = request.args.get('day', default=0, type=int)
    if day < 1 or day > len(study_plan):
        return jsonify({"error": f"Day must be 1-{len(study_plan)}"}), 400
    d = study_plan[day - 1]
    return jsonify({"day": day, "exercises": d["exercises"], "topic": d["topic"]})
