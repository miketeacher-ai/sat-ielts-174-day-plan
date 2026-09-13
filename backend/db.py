"""Database engine + session. SQLite locally, Postgres via DATABASE_URL in prod."""
import os
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _resolve_database_url() -> str:
    override = os.environ.get("DATABASE_URL", "").strip()
    if override:
        return override
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for base in (_ROOT, tempfile.gettempdir()):
        # Serverless filesystems are read-only: a makedirs failure here must
        # fall through to the temp dir, never crash the entrypoint import.
        d = os.path.join(base, "notes") if base == _ROOT else os.path.join(base, "sat-v2-notes")
        try:
            os.makedirs(d, exist_ok=True)
            probe = os.path.join(d, ".w")
            with open(probe, "w") as f:
                f.write("1")
            os.remove(probe)
            return f"sqlite:///{os.path.join(d, 'v2.db')}"
        except (OSError, IOError):
            continue
    raise RuntimeError("No writable location for the SQLite database")


DATABASE_URL = _resolve_database_url()

_engine_kwargs = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from backend import models  # noqa: F401  (register tables)

    Base.metadata.create_all(bind=engine)
