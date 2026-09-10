"""GET / — serves the SPA shell (used via vercel.json rewrite)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(ROOT, 'static')

app = Flask(__name__)


@app.route('/api/rootfn')
def handler():
    return send_from_directory(STATIC_DIR, 'index.html')
