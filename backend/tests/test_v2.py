"""v2 backend tests: auth, notes UUIDs + tombstones, progress LWW, SM-2, plan.

Run:  python3 backend/tests/test_v2.py   (or pytest)
"""
import os
import sys
import tempfile

_tmp = tempfile.mkdtemp(prefix="v2-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp, 'test.db')}"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient  # noqa: E402

from backend import models  # noqa: E402
from backend.db import SessionLocal  # noqa: E402
from backend.main import app  # noqa: E402

failures = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


c = TestClient(app)

check("health", c.get("/api/health").json() == {"status": "ok"})

plan = c.get("/api/plan").json()
check("plan loads", isinstance(plan, list) and len(plan) > 100, len(plan) if isinstance(plan, list) else type(plan))
days = c.get("/api/days").json()
check("days index matches plan", len(days) == len(plan) and all(set(d) == {"day", "topic", "word_count"} for d in days))
check("day ids contiguous", sorted(d["day"] for d in days) == list(range(1, len(days) + 1)))
check("word count 5000", sum(d["word_count"] for d in days) == 5000, sum(d["word_count"] for d in days))
check("day by value", c.get("/api/day/1").json().get("day") == 1)
check("day oob 404", c.get("/api/day/9999").status_code == 404)
check("random ok", len(c.get("/api/words/random?n=5").json()) == 5)
check("random n=0 rejected", c.get("/api/words/random?n=0").status_code == 422)
check("random n=51 rejected", c.get("/api/words/random?n=51").status_code == 422)
check("exercise ok", "exercises" in c.get("/api/exercise/1").json())
check("exercise oob 404", c.get("/api/exercise/9999").status_code == 404)

# --- auth ---
check("me without token 401", c.get("/api/auth/me").status_code == 401)
r = c.post("/api/auth/register", json={"email": "a@x.com", "password": "short"})
check("short password 422", r.status_code == 422, r.status_code)
r = c.post("/api/auth/register", json={"email": "a@x.com", "password": "password123"})
check("register 201 + token", r.status_code == 201 and "access_token" in r.json(), r.status_code)
r = c.post("/api/auth/register", json={"email": "a@x.com", "password": "password123"})
check("duplicate 409", r.status_code == 409, r.status_code)
r = c.post("/api/auth/login", json={"email": "a@x.com", "password": "wrong"})
check("bad login 401", r.status_code == 401, r.status_code)
token = c.post("/api/auth/login", json={"email": "a@x.com", "password": "password123"}).json()["access_token"]
H = {"Authorization": f"Bearer {token}"}
check("me 200", c.get("/api/auth/me", headers=H).json().get("email") == "a@x.com")
check("bad token 401", c.get("/api/auth/me", headers={"Authorization": "Bearer nope"}).status_code == 401)
check("notes need auth", c.get("/api/notes").status_code == 401)

# --- notes: client UUIDs preserved, tombstones ---
nid = "client-uuid-123"
r = c.post("/api/notes", json={"id": nid, "day": 1, "text": "hello"}, headers=H)
check("note id preserved", r.status_code == 201 and r.json()["id"] == nid, r.status_code)
r = c.post("/api/notes", json={"id": nid, "day": 1, "text": "again"}, headers=H)
check("re-post same id idempotent", r.status_code == 201 and r.json()["id"] == nid, r.status_code)
check("no dupes", [n["id"] for n in c.get("/api/notes", headers=H).json()] == [nid])
r = c.post("/api/notes", json={"id": "x", "day": 1, "text": ""}, headers=H)
check("empty text 422", r.status_code == 422, r.status_code)
r = c.put("/api/notes", json={"id": nid, "day": 2, "text": "edited"}, headers=H)
check("put updates", r.status_code == 200 and r.json()["text"] == "edited" and r.json()["day"] == 2, r.status_code)
r = c.put("/api/notes", json={"id": "brand-new", "day": 1, "text": "upsert-creates"}, headers=H)
check("put creates missing", r.status_code in (200, 201) and r.json()["id"] == "brand-new", r.status_code)
check("delete missing 404", c.request("DELETE", "/api/notes", json={"id": "nope"}, headers=H).status_code == 404)
check("delete ok", c.request("DELETE", "/api/notes", json={"id": nid}, headers=H).status_code == 200)
ids = [n["id"] for n in c.get("/api/notes", headers=H).json()]
check("tombstone hidden", nid not in ids and "brand-new" in ids, ids)

# --- progress LWW ---
check("progress empty", c.get("/api/progress", headers=H).json()["completed_days"] == [])
doc = {"completed_days": [1, 2], "mastered_words": ["abate"], "streak": 3, "updated_at": "2026-01-02T00:00:00"}
check("progress put", c.put("/api/progress", json=doc, headers=H).status_code == 200)
check("progress round-trip", c.get("/api/progress", headers=H).json()["streak"] == 3)
stale = dict(doc, streak=99, updated_at="2025-01-01T00:00:00")
check("stale put 409", c.put("/api/progress", json=stale, headers=H).status_code == 409)
check("stale not applied", c.get("/api/progress", headers=H).json()["streak"] == 3)

# --- SM-2 review ---
r = c.post("/api/review/grade", json={"word": "abate", "quality": 5}, headers=H).json()
check("sm2 first interval=1", r["i"] == 1 and r["n"] == 1, r)
r = c.post("/api/review/grade", json={"word": "abate", "quality": 5}, headers=H).json()
check("sm2 second interval=6", r["i"] == 6 and r["n"] == 2, r)
r = c.post("/api/review/grade", json={"word": "abate", "quality": 1}, headers=H).json()
check("sm2 fail resets", r["i"] == 1 and r["n"] == 0, r)
check("bad quality 422", c.post("/api/review/grade", json={"word": "abate", "quality": 9}, headers=H).status_code == 422)
db = SessionLocal()
import time as _t

past = int(_t.time() * 1000) - 10_000
db.add(models.Review(user_id=c.get("/api/auth/me", headers=H).json()["id"], word="oldo", n=2, e=2.5, i=6, d=past))
db.commit()
db.close()
due = c.get("/api/review/due", headers=H).json()
check("overdue listed", "oldo" in due["due"] and due["count"] >= 1, due)
Dord = dict(doc, mastered_words=["abate", "oldo"], updated_at="2026-01-03T00:00:00")
c.put("/api/progress", json=Dord, headers=H)
due = c.get("/api/review/due", headers=H).json()
check("mastered excluded from due", "oldo" not in due["due"], due)

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
