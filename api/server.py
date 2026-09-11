from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import json, os, random, time

app = Flask(__name__)
CORS(app)

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DATA_DIR = os.path.join(ROOT, 'data')


def _writable_notes_dir():
    """Notes dir with temp fallback (Vercel/serverless filesystems are read-only)."""
    primary = os.path.join(os.path.dirname(BASE), 'notes')
    try:
        os.makedirs(primary, exist_ok=True)
        probe = os.path.join(primary, '.w')
        with open(probe, 'w') as f:
            f.write('1')
        os.remove(probe)
        return primary
    except (OSError, IOError):
        import tempfile
        fallback = os.path.join(tempfile.gettempdir(), 'sat-ielts-notes')
        os.makedirs(fallback, exist_ok=True)
        return fallback


NOTES_DIR = _writable_notes_dir()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

words = load_json(os.path.join(DATA_DIR, 'words.json'))
study_plan = load_json(os.path.join(DATA_DIR, 'study_plan.json'))

# Token-aware interval config
TOKEN_INTERVAL_MS = int(os.environ.get('TOKEN_INTERVAL_MS', '2000'))
last_ai_call = 0

@app.route('/api/days')
def get_days():
    return jsonify([{"day": d["day"], "topic": d["topic"], "word_count": len(d["words"])} for d in study_plan])

@app.route('/api/plan')
def get_plan():
    return jsonify(study_plan)

@app.route('/api/words.json')
def get_words_file():
    return send_from_directory(DATA_DIR, 'words.json')

@app.route('/api/day/<int:day>')
def get_day(day):
    d = next((x for x in study_plan if x.get('day') == day), None)
    if d is None:
        return jsonify({"error": f"Day must be 1-{len(study_plan)}"}), 404
    return jsonify(d)

@app.route('/api/words/random')
def get_random_words():
    try:
        n = int(request.args.get('n', 10))
    except (TypeError, ValueError):
        return jsonify({"error": "Query param 'n' must be an integer"}), 400
    if n < 1 or n > 50:
        return jsonify({"error": "Query param 'n' must be 1-50"}), 400
    if n > len(words):
        return jsonify({"error": f"Only {len(words)} words available"}), 400
    return jsonify(random.sample(words, n))

@app.route('/api/exercise/<int:day>')
def get_exercise(day):
    d = next((x for x in study_plan if x.get('day') == day), None)
    if d is None:
        return jsonify({"error": f"Day must be 1-{len(study_plan)}"}), 404
    return jsonify({"day": day, "exercises": d["exercises"], "topic": d["topic"]})

@app.route('/api/progress', methods=['GET', 'POST'])
def progress():
    path = os.path.join(NOTES_DIR, 'progress.json')
    if request.method == 'POST':
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Progress body must be a JSON object"}), 400
        try:
            save_json(path, data)
        except OSError as e:
            return jsonify({"error": f"Could not save progress: {e}"}), 500
        return jsonify({"status": "saved"})
    if os.path.exists(path):
        try:
            return jsonify(load_json(path))
        except (json.JSONDecodeError, OSError) as e:
            return jsonify({"error": f"Could not read progress: {e}"}), 500
    return jsonify({"completed_days": [], "total_words_studied": 0})

@app.route('/api/notes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def notes():
    path = os.path.join(NOTES_DIR, 'notes.json')
    if request.method == 'GET':
        if os.path.exists(path):
            try:
                return jsonify(load_json(path))
            except (json.JSONDecodeError, OSError) as e:
                return jsonify({"error": f"Could not read notes: {e}"}), 500
        return jsonify([])
    if request.method == 'POST':
        data = load_json(path) if os.path.exists(path) else []
        if not isinstance(data, list):
            data = []
        note = request.get_json(silent=True)
        if not isinstance(note, dict):
            return jsonify({"error": "Note body must be a JSON object"}), 400
        # Preserve a unique client-supplied id (Date.now()) so the frontend
        # can reconcile; otherwise assign max+1.
        existing_ids = {n.get('id') for n in data if isinstance(n, dict)}
        if note.get('id') in (None, 0) or note.get('id') in existing_ids:
            note['id'] = max([n.get('id', 0) for n in data if isinstance(n, dict)] + [0]) + 1
        from datetime import datetime, timezone
        note.setdefault('created', datetime.now(timezone.utc).isoformat())
        data.append(note)
        try:
            save_json(path, data)
        except OSError as e:
            return jsonify({"error": f"Could not save notes: {e}"}), 500
        return jsonify(note)
    if request.method == 'PUT':
        data = load_json(path) if os.path.exists(path) else []
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
        try:
            save_json(path, data)
        except OSError as e:
            return jsonify({"error": f"Could not save notes: {e}"}), 500
        return jsonify(note)
    if request.method == 'DELETE':
        data = load_json(path) if os.path.exists(path) else []
        if not isinstance(data, list):
            data = []
        body = request.get_json(silent=True)
        if not isinstance(body, dict) or body.get('id') is None:
            return jsonify({"error": "DELETE body must be a JSON object with an 'id'"}), 400
        note_id = body.get('id')
        data = [n for n in data if not (isinstance(n, dict) and n.get('id') == note_id)]
        try:
            save_json(path, data)
        except OSError as e:
            return jsonify({"error": f"Could not save notes: {e}"}), 500
        return jsonify({"status": "deleted"})

@app.route('/api/token-status', methods=['GET', 'POST'])
def token_status():
    """Rate-limit helper. POST marks an AI call (sets last_ai_call to now);
    GET only reports. Frontend degrades to a local timer when unreachable."""
    global last_ai_call
    if request.method == 'POST':
        last_ai_call = time.time()
    now = time.time()
    elapsed = now - last_ai_call
    can_call = elapsed >= (TOKEN_INTERVAL_MS / 1000.0)
    return jsonify({
        "interval_ms": TOKEN_INTERVAL_MS,
        "seconds_since_last_call": round(elapsed, 1),
        "can_make_ai_call": can_call,
        "estimated_tokens_remaining": "high" if can_call else "wait"
    })

@app.route('/')
def index():
    return send_file(os.path.join(ROOT, 'index.html'))

@app.route('/data/<path:path>')
def static_files(path):
    return send_from_directory(DATA_DIR, path)

if __name__ == '__main__':
    os.makedirs(NOTES_DIR, exist_ok=True)
    print("Starting SAT/IELTS Study Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)