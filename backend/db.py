"""Database engine + session. SQLite locally, Postgres via DATABASE_URL in prod."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _DATA = os.path.join(_ROOT, "notes")
    os.makedirs(_DATA, exist_ok=True)
    DATABASE_URL = f"sqlite:///{os.path.join(_DATA, 'v2.db')}"

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
