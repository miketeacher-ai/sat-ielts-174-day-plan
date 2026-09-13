from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.db import get_db
from backend.security import current_user, hash_password, make_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut, status_code=201)
def register(body: schemas.RegisterIn, db: Session = Depends(get_db)):  # noqa: B008
    email = body.email.strip().lower()
    if db.query(models.User).filter_by(email=email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = models.User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from None
    db.refresh(user)
    return schemas.TokenOut(access_token=make_token(user.id))


@router.post("/login", response_model=schemas.TokenOut)
def login(body: schemas.LoginIn, db: Session = Depends(get_db)):  # noqa: B008
    user = db.query(models.User).filter_by(email=body.email.strip().lower()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return schemas.TokenOut(access_token=make_token(user.id))


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(current_user)):  # noqa: B008
    return schemas.UserOut(id=user.id, email=user.email)
