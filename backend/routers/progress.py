"""Progress: server copy is source of truth, last-write-wins on updated_at."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.db import get_db
from backend.security import current_user

router = APIRouter(prefix="/api/progress", tags=["progress"])

EMPTY = {
    "completed_days": [], "seen_words": [], "mastered_words": [], "wrong_words": [],
    "gates": {}, "streak": 0, "best_quiz": 0, "best_quiz_n": 0,
    "best_timed": 0, "best_timed_n": 0, "quizzes_taken": 0,
    "last_visit": None, "updated_at": None,
}


def _out(row: models.Progress) -> schemas.ProgressOut:
    return schemas.ProgressOut(
        completed_days=row.completed_days or [], seen_words=row.seen_words or [],
        mastered_words=row.mastered_words or [], wrong_words=row.wrong_words or [],
        gates=row.gates or {}, streak=row.streak or 0,
        best_quiz=row.best_quiz or 0, best_quiz_n=row.best_quiz_n or 0,
        best_timed=row.best_timed or 0, best_timed_n=row.best_timed_n or 0,
        quizzes_taken=row.quizzes_taken or 0, last_visit=row.last_visit, updated_at=row.updated_at,
    )


@router.get("", response_model=schemas.ProgressOut)
def get_progress(user: models.User = Depends(current_user), db: Session = Depends(get_db)):  # noqa: B008
    row = db.query(models.Progress).filter_by(user_id=user.id).first()
    if row is None:
        return schemas.ProgressOut(**EMPTY)
    return _out(row)


@router.put("", response_model=schemas.ProgressOut)
def put_progress(
    body: schemas.ProgressIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)  # noqa: B008
):
    row = db.query(models.Progress).filter_by(user_id=user.id).first()
    if row is None:
        row = models.Progress(user_id=user.id)
        db.add(row)
    elif row.updated_at and body.updated_at and body.updated_at < row.updated_at:
        raise HTTPException(status_code=409, detail="Stale progress document", headers={"X-Current-Updated-At": row.updated_at or ""})
    row.completed_days = body.completed_days
    row.seen_words = body.seen_words[-5000:]
    row.mastered_words = body.mastered_words
    row.wrong_words = body.wrong_words[-200:]
    row.gates = body.gates
    row.streak = body.streak
    row.best_quiz, row.best_quiz_n = body.best_quiz, body.best_quiz_n
    row.best_timed, row.best_timed_n = body.best_timed, body.best_timed_n
    row.quizzes_taken = body.quizzes_taken
    row.last_visit = body.last_visit
    row.updated_at = body.updated_at
    db.commit()
    db.refresh(row)
    return _out(row)
