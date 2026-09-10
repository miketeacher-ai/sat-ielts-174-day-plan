"""Vercel serverless entry point — exposes the Flask `app` object.

Local development still uses `api/server.py` directly:
    python api/server.py
On Vercel, `vercel.json` rewrites all routes here and the platform
serves `app`. Runtime data files are bundled via `includeFiles`.
User notes/progress fall back to the OS temp dir on read-only
filesystems (see server.py); the frontend additionally mirrors all
state in localStorage, so the deployed app works fully client-side.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app  # noqa: F401  (consumed by the Vercel Python runtime)
