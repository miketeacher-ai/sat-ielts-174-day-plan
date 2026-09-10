"""Shared data layer for the Vercel serverless API functions.

Loads the word data once per (warm) instance. Notes/progress writes go
to the project notes/ dir locally and fall back to the OS temp dir on
read-only serverless filesystems (the frontend mirrors everything in
localStorage, so the app works fully either way).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')


def _load(name):
    with open(os.path.join(DATA_DIR, name), encoding='utf-8') as f:
        return json.load(f)


words = _load('words.json')
study_plan = _load('study_plan.json')


def notes_dir():
    primary = os.path.join(ROOT, 'notes')
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


NOTES_DIR = notes_dir()


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
