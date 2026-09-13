"""Server-side SM-2 scheduling: grade a word, list what's due."""
import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.db import get_db
from backend.security import current_user

router = APIRouter(prefix="/api/review", tags=["review"])

DAY_MS = 86_400_000


def sm2_step(n: int, e: float, i: int, q: int, now_ms: int) -> tuple[int, float, int, int]:
    q = max(0, min(5, q))
    if q >= 3:
        if n == 0:
            i = 1
        elif n == 1:
            i = 6
        else:
            i = max(1, round(i * e))
        n += 1
        e = max(1.3, e + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    else:
        n, i = 0, 1
    return n, e, i, now_ms + i * DAY_MS


@router.post("/grade", response_model=schemas.ReviewOut)
def grade(
    body: schemas.GradeIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)  # noqa: B008
):
    now_ms = int(time.time() * 1000)
    row = db.query(models.Review).filter_by(user_id=user.id, word=body.word).first()
    if row is None:
        row = models.Review(user_id=user.id, word=body.word)
        db.add(row)
    row.n, row.e, row.i, row.d = sm2_step(row.n or 0, row.e or 2.5, row.i or 0, body.quality, now_ms)
    db.commit()
    db.refresh(row)
    return schemas.ReviewOut(word=row.word, n=row.n, e=row.e, i=row.i, d=row.d)


@router.get("/due", response_model=schemas.DueOut)
def due(user: models.User = Depends(current_user), db: Session = Depends(get_db)):  # noqa: B008
    now_ms = int(time.time() * 1000)
    prog = db.query(models.Progress).filter_by(user_id=user.id).first()
    mastered = set(prog.mastered_words) if prog and prog.mastered_words else set()
    rows = (
        db.query(models.Review)
        .filter_by(user_id=user.id)
        .filter(models.Review.d <= now_ms)
        .order_by(models.Review.d)
        .all()
    )
    words = [r.word for r in rows if r.word not in mastered]
    return schemas.DueOut(due=words, count=len(words))
