"""GET / — serves the SPA shell (used via vercel.json rewrite)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/api/rootfn', methods=['GET'])
def handler():
    return send_from_directory(ROOT, 'index.html')
