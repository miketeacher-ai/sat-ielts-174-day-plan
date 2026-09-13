"""Notes with client UUIDs (never reassigned) + tombstone deletes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.db import get_db
from backend.security import current_user

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("", response_model=list[schemas.NoteOut])
def list_notes(user: models.User = Depends(current_user), db: Session = Depends(get_db)):  # noqa: B008
    rows = (
        db.query(models.Note)
        .filter_by(user_id=user.id)
        .filter(models.Note.deleted_at.is_(None))
        .order_by(models.Note.id)
        .all()
    )
    return [schemas.NoteOut(id=r.id, day=r.day, text=r.text, created=r.created, updated_at=r.updated_at) for r in rows]


@router.post("", response_model=schemas.NoteOut, status_code=201)
def create_note(
    body: schemas.NoteIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)  # noqa: B008
):
    existing = db.query(models.Note).filter_by(id=body.id, user_id=user.id).first()
    if existing is not None:
        if existing.deleted_at is not None:
            existing.deleted_at = None
            existing.day, existing.text = body.day, body.text
            existing.created = body.created or existing.created
            existing.updated_at = body.updated_at or _now()
            db.commit()
            db.refresh(existing)
        return schemas.NoteOut(
            id=existing.id, day=existing.day, text=existing.text, created=existing.created, updated_at=existing.updated_at
        )
    row = models.Note(
        id=body.id, user_id=user.id, day=body.day, text=body.text,
        created=body.created or _now(), updated_at=body.updated_at or _now(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return schemas.NoteOut(id=row.id, day=row.day, text=row.text, created=row.created, updated_at=row.updated_at)


@router.put("", response_model=schemas.NoteOut)
def upsert_note(
    body: schemas.NoteIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)  # noqa: B008
):
    row = db.query(models.Note).filter_by(id=body.id, user_id=user.id).first()
    if row is None:
        return create_note(body, user, db)
    row.day, row.text = body.day, body.text
    if body.created:
        row.created = body.created
    row.updated_at = body.updated_at or _now()
    row.deleted_at = None
    db.commit()
    db.refresh(row)
    return schemas.NoteOut(id=row.id, day=row.day, text=row.text, created=row.created, updated_at=row.updated_at)


@router.delete("", response_model=dict)
def delete_note(
    body: schemas.IdIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)  # noqa: B008
):
    row = db.query(models.Note).filter_by(id=body.id, user_id=user.id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")
    row.deleted_at = _now()
    db.commit()
    return {"status": "deleted"}
