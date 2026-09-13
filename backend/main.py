"""FastAPI application: all API routes + static frontend (local single-port dev).

On Vercel the root `app.py` entrypoint re-exports `app` and static files are
served by the platform; the `/` + `/data/*` fallbacks below only trigger
when no static file matched (local dev single-process runs).
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.db import init_db
from backend.routers import auth, notes, plan, progress, review

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "frontend", "dist")

app = FastAPI(title="SAT & IELTS Vocab v2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth.router)
app.include_router(plan.router)
app.include_router(notes.router)
app.include_router(progress.router)
app.include_router(review.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if os.path.isdir(DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST, "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    def index():
        return FileResponse(os.path.join(DIST, "index.html"))
