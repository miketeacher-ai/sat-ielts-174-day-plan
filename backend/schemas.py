"""Pydantic schemas — validation at the boundary (400s/422s, never 500s)."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str


class NoteIn(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    day: Optional[int] = None
    text: str = Field(min_length=1, max_length=2000)
    created: Optional[str] = None
    updated_at: Optional[str] = None


class NoteOut(NoteIn):
    pass


class IdIn(BaseModel):
    id: str = Field(min_length=1, max_length=64)


class ProgressIn(BaseModel):
    completed_days: List[int] = []
    seen_words: List[str] = []
    mastered_words: List[str] = []
    wrong_words: List[str] = []
    gates: Dict[str, Any] = {}
    streak: int = 0
    best_quiz: int = 0
    best_quiz_n: int = 0
    best_timed: int = 0
    best_timed_n: int = 0
    quizzes_taken: int = 0
    last_visit: Optional[str] = None
    updated_at: Optional[str] = None


class ProgressOut(ProgressIn):
    pass


class GradeIn(BaseModel):
    word: str = Field(min_length=1, max_length=64)
    quality: int = Field(ge=0, le=5)


class ReviewOut(BaseModel):
    word: str
    n: int
    e: float
    i: int
    d: int


class DueOut(BaseModel):
    due: List[str]
    count: int
