# SAT & IELTS Vocabulary Plan

5000 real B1+ exam words across build-derived theme-based days (~30/day,
currently 173 — see `data/build_report.json`), 2 exercises
per day, compulsory checkpoint + final quizzes, animated flashcards, notes,
quizzes, review queue, and a data-rich dashboard — backed by a FastAPI +
SQLite/Postgres v2 API with JWT auth and server-side spaced repetition.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --port 5000
# http://localhost:5000  (API + frontend; user data in notes/v2.db)
```

## Deploy to Vercel

```bash
npm i -g vercel
vercel login
vercel --prod
```

The repo ships `vercel.json` (bundles word data via `includeFiles`) and
pinned `requirements.txt`. Vercel applies its Python framework preset to
the root entrypoint `app.py`, which re-exports the FastAPI app from
`backend/main.py` (all routes: `/api/*`, plus `/` + `/assets/*` when
`frontend/dist` exists). Set `DATABASE_URL` (Postgres) and `SECRET_KEY`
in production; without them the app falls back to an instance-local
SQLite database.
Notes:

- Serverless filesystems are read-only — without `DATABASE_URL` the backend
  falls back to the OS temp dir, so server-side state is per-instance.
  Set Postgres for real multi-user deployments.
- The bundled single-page frontend still mirrors **all** state in
  `localStorage`, so the app works fully client-side regardless.
- First cold start parses ~4 MB of word JSON; subsequent requests are warm.

## Deploy to GitHub

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

`notes/*.json` (personal study data) and generator backups are git-ignored.

## Layout

| Path | What |
|---|---|
| `index.html` | Bundled study app — UI + CSS + JS (served at `/` until the Vite frontend lands) |
| `app.py` | Deploy entrypoint (re-exports `backend.main:app`) |
| `backend/` | FastAPI v2 API: JWT auth, notes (client UUIDs + tombstones), LWW progress, server-side SM-2, plan/seed endpoints |
| `backend/tests/test_v2.py` | API suite: auth, sync rules, SM-2, validation (`python3 backend/tests/test_v2.py`) |
| `data/words.json` | 5000 words: definition, POS, difficulty 3–5, synonyms, example, category, theme, day |
| `data/study_plan.json` | Theme-based days (~30 words each): topic, 2 exercises (count is build-derived) |
| `data/sources/` | Provenance: SAT lists, AWL, English-dict filter, curated core |
| `notes/` | Local runtime data (git-ignored) |
| `rebuild.py` | Reproducible data build (WordNet + wordfreq, zero model calls) |
| `gen_core.py` | Builds the 125-word curated core (`data/sources/words_core.json`) |
| `test_quiz.js` / `test_focus.js` | Quiz + focus regression tests (`npm test`) |
| `DESIGN.md` / `tokens.json` | Token spec (lint-clean) + DTCG export |

## API (v2, auth via `Authorization: Bearer <token>`)

- `POST /api/auth/register` · `POST /api/auth/login` · `GET /api/auth/me`
- `GET /api/days` — day index (topic, word count)
- `GET /api/plan` — full plan
- `GET /api/day/<n>`, `/api/words/random?n=`, `/api/exercise/<n>` — public
- `GET/POST/PUT/DELETE /api/notes` — client UUIDs, tombstone deletes
- `GET/PUT /api/progress` — server copy wins; stale writes get 409
- `POST /api/review/grade` · `GET /api/review/due` — server-side SM-2

## Data

3393 SAT / 1300 IELTS (AWL-first) / 307 Both · 29 WordNet-derived themes ·
frequency-graded difficulty · sense-ranked definitions · validated exercises.
(Quotas in `rebuild.py` target 2200/1300/1500; the Both overlap in the
sources is smaller, so shortfalls spill into SAT — the build prints the
actual fill per category.)

```bash
python3 -m pip install nltk wordfreq
python3 rebuild.py            # hard-fails on quota/field/quiz violations
npm test                      # quiz + focus regression tests
python3 backend/tests/test_v2.py  # v2 API suite
```

## License

MIT — see `LICENSE`.
