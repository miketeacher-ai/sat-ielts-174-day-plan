"""GET/POST/PUT/DELETE /api/notes — learner notes."""
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request  # noqa: E402

from _core import NOTES_DIR, load_json, save_json  # noqa: E402

app = Flask(__name__)


@app.route('/api/notes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def handler():
    path = os.path.join(NOTES_DIR, 'notes.json')
    if request.method == 'GET':
        return jsonify(load_json(path, []))
    if request.method == 'POST':
        data = load_json(path, [])
        note = request.json
        note['id'] = max([n.get('id', 0) for n in data] + [0]) + 1
        note['created'] = datetime.now(timezone.utc).isoformat()
        data.append(note)
        save_json(path, data)
        return jsonify(note)
    if request.method == 'PUT':
        data = load_json(path, [])
        note = request.json
        for i, n in enumerate(data):
            if n.get('id') == note.get('id'):
                data[i] = note
                break
        save_json(path, data)
        return jsonify(note)
    if request.method == 'DELETE':
        data = load_json(path, [])
        note_id = request.json.get('id')
        save_json(path, [n for n in data if n.get('id') != note_id])
        return jsonify({"status": "deleted"})
