"""Vercel Flask entrypoint.

Vercel detects `flask` in requirements.txt and applies the Flask preset,
which takes precedence over file-based `/api` functions and requires an
entrypoint exposing `app` at the project root (it only looks in
`app.py`/`server.py`/etc. at the root or in `src/`/`app/` — NOT in `api/`).
Without this file the deployment has no entrypoint and no API route comes
up, even though the per-file functions under `api/` look correct.

The full app (all routes: `/`, `/api/*`, `/data/*`) lives in
`api/server.py`, which is also what local dev runs (`python api/server.py`);
this module just re-exports its `app`.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "api"))

from server import app  # noqa: E402,F401
