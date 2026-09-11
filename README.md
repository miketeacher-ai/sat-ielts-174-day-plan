# SAT & IELTS 174-Day Vocabulary Plan

5000 real B1+ exam words across 174 theme-based days (~30/day), 2 exercises
per day, compulsory checkpoint + final quizzes, animated flashcards, notes,
quizzes, review queue, and a data-rich dashboard — in a single-page app
with a Flask backend.

## Run locally

```bash
pip install -r requirements.txt
python api/server.py
# http://localhost:5000
```

## Deploy to Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

The repo ships `vercel.json` (all routes → the Flask app in `api/index.py`,
word data bundled via `includeFiles`) and pinned `requirements.txt`.
Notes:

- Serverless filesystems are read-only — the backend stores notes/progress
  in the OS temp dir there, so server-side state is per-instance.
- The frontend mirrors **all** state (progress, mastered words, gates,
  notes, quiz bests) in `localStorage` and merges on load, so the deployed
  app works fully client-side regardless.
- First cold start parses ~3 MB of word JSON; subsequent requests are warm.

## Deploy to GitHub

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

`notes/*.json` (personal study data) and generator backups are git-ignored.

## Layout

| Path | What |
|---|---|
| `index.html` | The app — UI + CSS + JS, no build step, no CDN JS (served at `/` everywhere) |
| `api/server.py` | Flask backend + JSON API (local dev; also serves `/data/*`) |
| `api/*.py` | Vercel serverless endpoints (one Flask app per route) + shared `_core.py` |
| `data/words.json` | 5000 words: definition, POS, difficulty 3–5, synonyms, example, category, theme, day |
| `data/study_plan.json` | 174 days: theme topic, ~30 words, 2 exercises |
| `data/sources/` | Provenance: SAT lists, AWL, English-dict filter, curated core |
| `notes/` | Local runtime data (git-ignored) |
| `rebuild.py` | Reproducible data build (WordNet + wordfreq, zero model calls) |
| `gen_core.py` | Builds the 125-word curated core (`data/sources/words_core.json`) |
| `test_quiz.js` / `test_focus.js` | Regression tests (`node test_*.js`) |
| `DESIGN.md` / `tokens.json` | Token spec (lint-clean) + DTCG export |

## API

- `GET /api/days` — day index (topic, word count)
- `GET /api/plan` — full plan
- `GET /api/words.json` — raw word list (local Flask)
- `GET /api/day/<n>`, `/api/words/random`, `/api/exercise/<n>`, `/api/token-status` — local Flask only
- `GET/POST /api/progress` · `GET/POST/PUT/DELETE /api/notes`

## Data

3365 SAT / 1300 IELTS (AWL-first) / 335 Both · 29 WordNet-derived themes ·
frequency-graded difficulty · sense-ranked definitions · validated exercises.

```bash
python3 -m pip install nltk wordfreq
python3 rebuild.py
node test_quiz.js
```

## License

MIT — see `LICENSE`.
