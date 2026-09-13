"""Seed content: words + study plan from JSON, lazily loaded and cached."""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_ROOT, "data")

_cache: dict = {}


def _load(name: str):
    if name not in _cache:
        with open(os.path.join(_DATA, name), encoding="utf-8") as f:
            _cache[name] = json.load(f)
    return _cache[name]


def get_words():
    return _load("words.json")


def get_plan():
    return _load("study_plan.json")


def find_day(day: int):
    for d in get_plan():
        if d.get("day") == day:
            return d
    return None
