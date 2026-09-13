"""Password hashing (pbkdf2 — no native deps) + JWT bearer auth."""
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend import models
from backend.db import get_db

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-change-in-production-xyz")
ALGORITHM = "HS256"
ACCESS_DAYS = 30

_pwd = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
_bearer = HTTPBearer(auto_error=False)


def hash_password(pw: str) -> str:
    return _pwd.hash(pw)


def verify_password(pw: str, hashed: str) -> bool:
    return _pwd.verify(pw, hashed)


def make_token(user_id: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=ACCESS_DAYS)
    return jwt.encode({"sub": user_id, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
) -> models.User:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from None
    user = db.get(models.User, uid) if uid else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return user
