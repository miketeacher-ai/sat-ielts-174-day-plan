"""GET/POST /api/progress — study progress document."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request  # noqa: E402

from _core import NOTES_DIR, load_json, save_json  # noqa: E402

app = Flask(__name__)


@app.route('/api/progress', methods=['GET', 'POST'])
def handler():
    path = os.path.join(NOTES_DIR, 'progress.json')
    if request.method == 'POST':
        save_json(path, request.json)
        return jsonify({"status": "saved"})
    return jsonify(load_json(path, {"completed_days": [], "total_words_studied": 0}))
