from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json, os, random

app = Flask(__name__, static_folder='../static', static_url_path='')
CORS(app)

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), 'data')


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
    if day < 1 or day > len(study_plan):
        return jsonify({"error": f"Day must be 1-{len(study_plan)}"}), 400
    d = study_plan[day - 1]
    return jsonify(d)

@app.route('/api/words/random')
def get_random_words():
    n = min(int(request.args.get('n', 10)), 50)
    return jsonify(random.sample(words, n))

@app.route('/api/exercise/<int:day>')
def get_exercise(day):
    if day < 1 or day > len(study_plan):
        return jsonify({"error": f"Day must be 1-{len(study_plan)}"}), 400
    d = study_plan[day - 1]
    return jsonify({"day": day, "exercises": d["exercises"], "topic": d["topic"]})

@app.route('/api/progress', methods=['GET', 'POST'])
def progress():
    path = os.path.join(NOTES_DIR, 'progress.json')
    if request.method == 'POST':
        data = request.json
        save_json(path, data)
        return jsonify({"status": "saved"})
    if os.path.exists(path):
        return jsonify(load_json(path))
    return jsonify({"completed_days": [], "total_words_studied": 0})

@app.route('/api/notes', methods=['GET', 'POST', 'PUT', 'DELETE'])
def notes():
    path = os.path.join(NOTES_DIR, 'notes.json')
    if request.method == 'GET':
        if os.path.exists(path):
            return jsonify(load_json(path))
        return jsonify([])
    if request.method == 'POST':
        data = load_json(path) if os.path.exists(path) else []
        note = request.json
        note['id'] = max([n.get('id', 0) for n in data] + [0]) + 1
        from datetime import datetime, timezone
        note['created'] = datetime.now(timezone.utc).isoformat()
        data.append(note)
        save_json(path, data)
        return jsonify(note)
    if request.method == 'PUT':
        data = load_json(path) if os.path.exists(path) else []
        note = request.json
        for i, n in enumerate(data):
            if n.get('id') == note.get('id'):
                data[i] = note
                break
        save_json(path, data)
        return jsonify(note)
    if request.method == 'DELETE':
        data = load_json(path) if os.path.exists(path) else []
        note_id = request.json.get('id')
        data = [n for n in data if n.get('id') != note_id]
        save_json(path, data)
        return jsonify({"status": "deleted"})

@app.route('/api/token-status')
def token_status():
    global last_ai_call
    import time
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
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    os.makedirs(NOTES_DIR, exist_ok=True)
    print("Starting SAT/IELTS Study Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)