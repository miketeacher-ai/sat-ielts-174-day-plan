"""Backend smoke test: routing, validation, notes id stability.

Run:  python3 -m pip install flask flask-cors   (once)
      python3 test_api.py
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))

import server  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


tmp = tempfile.mkdtemp(prefix="sat-test-")
server.NOTES_DIR = tmp
client = server.app.test_client()

r = client.get("/api/plan")
plan = r.get_json()
check("plan 200 + matches days", r.status_code == 200 and isinstance(plan, list) and len(plan) > 100, r.status_code)

r = client.get("/api/days")
days = r.get_json()
check("days index matches plan", r.status_code == 200 and len(days) == len(plan), r.status_code)

r = client.get("/api/day/1")
check("day by value (not index)", r.status_code == 200 and r.get_json().get("day") == 1, r.status_code)
r = client.get("/api/day/9999")
check("day out of range 404", r.status_code == 404, r.status_code)

r = client.get("/api/words/random?n=5")
check("random n=5", r.status_code == 200 and len(r.get_json()) == 5, r.status_code)
r = client.get("/api/words/random?n=abc")
check("random n=abc 400", r.status_code == 400, r.status_code)
r = client.get("/api/words/random?n=0")
check("random n=0 400", r.status_code == 400, r.status_code)
r = client.get("/api/words/random?n=51")
check("random n=51 400", r.status_code == 400, r.status_code)

r = client.get("/api/exercise/1")
check("exercise day 1", r.status_code == 200 and "exercises" in r.get_json(), r.status_code)
r = client.get("/api/exercise/9999")
check("exercise out of range 404", r.status_code == 404, r.status_code)

# Notes: client-supplied unique ids are preserved (no duplicate on merge).
r = client.post("/api/notes", json={"id": 123456, "day": 1, "text": "hello"})
check("note id preserved", r.status_code == 200 and r.get_json().get("id") == 123456, r.get_data(as_text=True)[:120])
r = client.post("/api/notes", json={"id": 123456, "day": 1, "text": "dup id"})
check("colliding id reassigned", r.status_code == 200 and r.get_json().get("id") != 123456, r.get_data(as_text=True)[:120])
r = client.get("/api/notes")
ids = [n.get("id") for n in r.get_json()]
check("note ids unique", len(ids) == len(set(ids)) == 2, ids)
r = client.post("/api/notes", json=["not", "an", "object"])
check("note non-object 400", r.status_code == 400, r.status_code)
r = client.delete("/api/notes", json={})
check("delete without id 400", r.status_code == 400, r.status_code)
r = client.put("/api/notes", json={"id": 999999, "text": "ghost"})
check("put missing note 404", r.status_code == 404, r.status_code)

# Progress: must be an object.
r = client.post("/api/progress", json=["nope"])
check("progress non-object 400", r.status_code == 400, r.status_code)
doc = {"completed_days": [1], "updated_at": "2026-01-01T00:00:00"}
r = client.post("/api/progress", json=doc)
check("progress save", r.status_code == 200, r.status_code)
r = client.get("/api/progress")
check("progress round-trip", r.status_code == 200 and r.get_json().get("completed_days") == [1], r.status_code)

# Token status: POST marks, GET reports.
r = client.post("/api/token-status")
j = r.get_json()
check("token just marked -> cooling down", r.status_code == 200 and j.get("can_make_ai_call") is False, j)
server.last_ai_call = 0
r = client.get("/api/token-status")
j = r.get_json()
check("token idle -> ready", r.status_code == 200 and j.get("can_make_ai_call") is True, j)

# Corrupt progress file degrades to 500 with JSON error, not a traceback page.
with open(os.path.join(tmp, "progress.json"), "w") as f:
    f.write("{broken")
r = client.get("/api/progress")
check("corrupt progress handled", r.status_code == 500 and "error" in r.get_json(), r.status_code)

r = client.get("/")
check("index serves", r.status_code == 200, r.status_code)

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
