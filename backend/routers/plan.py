import random

from fastapi import APIRouter, HTTPException, Query

from backend import seed

router = APIRouter(prefix="/api", tags=["plan"])


@router.get("/plan")
def get_plan():
    return seed.get_plan()


@router.get("/days")
def get_days():
    return [{"day": d["day"], "topic": d["topic"], "word_count": len(d["words"])} for d in seed.get_plan()]


@router.get("/day/{day}")
def get_day(day: int):
    d = seed.find_day(day)
    if d is None:
        raise HTTPException(status_code=404, detail=f"Day must be 1-{len(seed.get_plan())}")
    return d


@router.get("/words/random")
def get_random_words(n: int = Query(default=10, ge=1, le=50)):
    words = seed.get_words()
    if n > len(words):
        raise HTTPException(status_code=400, detail=f"Only {len(words)} words available")
    return random.sample(words, n)


@router.get("/exercise/{day}")
def get_exercise(day: int):
    d = seed.find_day(day)
    if d is None:
        raise HTTPException(status_code=404, detail=f"Day must be 1-{len(seed.get_plan())}")
    return {"day": day, "exercises": d["exercises"], "topic": d["topic"]}
