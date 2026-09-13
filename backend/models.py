"""SQLAlchemy models. Words/days stay in seed JSON; the DB owns user data."""
import uuid

from sqlalchemy import JSON, BigInteger, Column, DateTime, Float, Integer, String, Text, UniqueConstraint, func

from backend.db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class User(Base):
    __tablename__ = "users"

    id = Column(String(32), primary_key=True, default=_uuid)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Note(Base):
    """Client-generated UUID primary key — the server never reassigns ids."""

    __tablename__ = "notes"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(32), nullable=False, index=True)
    day = Column(Integer, nullable=True)
    text = Column(Text, nullable=False)
    created = Column(String(64), nullable=True)
    updated_at = Column(String(64), nullable=True)
    deleted_at = Column(String(64), nullable=True)  # tombstone; hidden from GET

    __table_args__ = (UniqueConstraint("id", "user_id", name="uq_note_user"),)


class Progress(Base):
    """One row per user; server copy is source of truth, LWW on updated_at."""

    __tablename__ = "progress"

    user_id = Column(String(32), primary_key=True)
    completed_days = Column(JSON, default=list, nullable=False)
    seen_words = Column(JSON, default=list, nullable=False)
    mastered_words = Column(JSON, default=list, nullable=False)
    wrong_words = Column(JSON, default=list, nullable=False)
    gates = Column(JSON, default=dict, nullable=False)
    streak = Column(Integer, default=0, nullable=False)
    best_quiz = Column(Integer, default=0, nullable=False)
    best_quiz_n = Column(Integer, default=0, nullable=False)
    best_timed = Column(Integer, default=0, nullable=False)
    best_timed_n = Column(Integer, default=0, nullable=False)
    quizzes_taken = Column(Integer, default=0, nullable=False)
    last_visit = Column(String(16), nullable=True)
    updated_at = Column(String(64), nullable=True)


class Review(Base):
    """Server-side SM-2 state per user+word. due `d` is epoch millis."""

    __tablename__ = "reviews"

    user_id = Column(String(32), primary_key=True)
    word = Column(String(64), primary_key=True)
    n = Column(Integer, default=0, nullable=False)
    e = Column(Float, default=2.5, nullable=False)
    i = Column(Integer, default=0, nullable=False)
    d = Column(BigInteger, default=0, nullable=False)
