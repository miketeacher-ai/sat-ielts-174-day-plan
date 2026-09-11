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
        data = load_json(path, [])
        return jsonify(data if isinstance(data, list) else [])
    if request.method == 'POST':
        data = load_json(path, [])
        if not isinstance(data, list):
            data = []
        note = request.get_json(silent=True)
        if not isinstance(note, dict):
            return jsonify({"error": "Note body must be a JSON object"}), 400
        # Preserve a unique client-supplied id so the frontend can reconcile.
        existing_ids = {n.get('id') for n in data if isinstance(n, dict)}
        if note.get('id') in (None, 0) or note.get('id') in existing_ids:
            note['id'] = max([n.get('id', 0) for n in data if isinstance(n, dict)] + [0]) + 1
        note.setdefault('created', datetime.now(timezone.utc).isoformat())
        data.append(note)
        save_json(path, data)
        return jsonify(note)
    if request.method == 'PUT':
        data = load_json(path, [])
        if not isinstance(data, list):
            data = []
        note = request.get_json(silent=True)
        if not isinstance(note, dict) or note.get('id') is None:
            return jsonify({"error": "Note body must be a JSON object with an 'id'"}), 400
        for i, n in enumerate(data):
            if isinstance(n, dict) and n.get('id') == note.get('id'):
                data[i] = note
                break
        else:
            return jsonify({"error": "Note not found"}), 404
        save_json(path, data)
        return jsonify(note)
    if request.method == 'DELETE':
        data = load_json(path, [])
        if not isinstance(data, list):
            data = []
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get('id') is None:
            return jsonify({"error": "DELETE body must be a JSON object with an 'id'"}), 400
        note_id = body.get('id')
        save_json(path, [n for n in data if not (isinstance(n, dict) and n.get('id') == note_id)])
        return jsonify({"status": "deleted"})
