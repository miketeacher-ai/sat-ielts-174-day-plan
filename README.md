# SAT & IELTS 60-Day Vocabulary Study Plan

5000 real exam words · 60 days (~83/day) · 2 exercises per day. Single-pageuint
animated UI with flip cards, notes, and progress tracking, backed by Flask.

## Layout

| Path | What |
|---|---|
| `static/index.html` | The app (single file: UI + CSS + JS) |
| `api/server.py` | Flask backend + JSON API |
| `data/words.json` | 5000 words: word, definition, POS, difficulty 1–5, synonyms, example, category, day |
| `data/study_plan.json` | 60 days: topic, words, 2 exercises |
| `data/sources/` | Provenance: SAT lists, AWL, English dict filter |
| `notes/` | User data: `notes.json`, `progress.json` (created at runtime) |
| `rebuild.py` | Data build script (reproducible) |

## Word data (all real, validated)

- **3365 SAT** — 6000-word SAT list + SAT word-of-the-day CSV, validity-filtered
- **1300 IELTS** — Academic Word List headwords/families first
- **335 Both** — words in SAT sources *and* AWL
- Definitions: source-authored, else WordNet (sense-ranked by attested usage)
- Difficulty 1–5 from word-frequency bands; days sorted easy → hard

Rebuild: `python3 rebuild.py` (needs `nltk` + `wordfreq`, downloads WordNet once).

## Run

```
pip install -r requirements.txt
python api/server.py   # http://localhost:5000
```

## API

- `GET /api/days` — day index (topic, word count)
- `GET /api/plan` — full 60-day plan
- `GET /api/day/<1-60>` — one day with words + exercises
- `GET /api/words.json` — raw word list
- `GET /api/words/random?n=` — random words (max 50)
- `GET/POST /api/progress` · `GET/POST/PUT/DELETE /api/notes`
- `GET /api/token-status` — AI-call throttle state (2 s interval guard)

## Notes

- No build step, no CDN JS: open `static/index.html` via the server only
  (fetches `/api/*`; `file://` won't work).
- Exercise types: `fill_in_blank`, `synonym_match`, `definition_match`
  (fallback when a word has no distinct synonym).
- Cards with no close synonym say so instead of echoing the word.
