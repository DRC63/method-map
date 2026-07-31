# P3MAI Method Map

An interactive reference tool that renders a project-management method as a
navigable network graph. v1 ships **PRINCE2 7**: 7 processes and 41 activities
cross-referenced to management team roles, practices, management approaches and
management products — the relationships from the PRINCE2/MSP cross-reference
skeleton, made explorable.

Built to match the PMO Service app (FastAPI + SQLite backend, React/Vite
frontend, single-origin Docker deploy) and cross-linked with the P3MAI website.

## What it does

Two complementary views over the same data:

- **Method Explorer** — the interdependency **network graph** (below).
- **Project Lifecycle** — the same processes laid out **in time**: the canonical
  PRINCE2 process model, with time running left→right (Pre-project → Initiation →
  Delivery stages ⟳ → Final stage) across three swimlanes (Directing / Managing /
  Delivering). Click a process to see its activities in sequence; jump straight to
  any of them in the graph.

- **Layered network graph** (`react-force-graph-2d`) — colour-coded nodes per
  entity type; toggle any layer on/off. With Activities hidden, the graph shows
  **indirect (co-occurrence) links** — two elements connect when they share an
  activity — so you can study Roles↔Practices, Roles↔Products, etc. on their own.
- **Detail panel** — click a node to see every relationship, grouped and labelled
  with the standard codes (C/P/N for roles/practices/approaches; I/O/U/A for
  products), with the owning process for incoming links.
- **Search** across all entities; **confidence flags** ("indicative" vs
  "confirmed") surfaced as a dashed ring, per the cross-reference caveats.
- **Authoring mode** — a single admin password unlocks add/edit/delete of
  entities and relationships (e.g. to populate a future MSP framework, or
  overtype an indicative code once SME-verified).
- **Exports** — graph as PNG, per-entity branded PDF summary, and the (optionally
  focused) cross-reference data as CSV / Excel.

## Architecture

- **Data model** is framework-agnostic: `frameworks` → `entities` (typed:
  process / activity / role / practice / approach / product; activities point at
  their process via `parent_id`) → `relationships` (from an activity to a target,
  with a code + confidence). MSP or any other framework drops in as another seed
  file with zero code changes.
- **Seed** is a self-contained JSON file per framework in
  `backend/app/seed_data/` (generated from the source spreadsheet). The app
  auto-seeds an empty database on first boot, so a fresh/ephemeral deploy comes
  up populated. `python -m app.seed --force` wipes and reseeds.

## Running locally

Both dev servers are registered in the working-directory `.claude/launch.json`
as `method-map-backend` (port 8002) and `method-map-frontend` (port 5175) —
prefer `preview_start` with those names.

**Backend** (terminal 1):
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload --port 8002
```
API docs: http://localhost:8002/docs

**Frontend** (terminal 2):
```powershell
cd frontend
npm install
npm run dev -- --port 5175
```
App: http://localhost:5175 (proxies `/api/*` to the backend on port 8002)

The website (separate repo, `../../business-website`) is linked via the "Back to
Website" item in the sidebar; the link auto-detects `localhost` vs. the real
domain. For cross-linking to work locally, serve the website over HTTP
(`business-website` launch config runs `python -m http.server 4173`).

## Authoring mode

Set `ADMIN_PASSWORD` in `backend/.env` (defaults to `change-me` — **change it
before deploying**). In the app, open **Authoring & Admin**, enter the password,
then edit from the Explorer. This is a lightweight gate to stop casual edits on
an open deployment, not a full account system.

## Tests

**Backend** (pytest, isolated per-test SQLite DB — never touches `methodmap.db`):
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

**Frontend** (Vitest + React Testing Library):
```powershell
cd frontend
npm test
```

## Production deployment

Same single-origin pattern as the PMO app: the backend serves the built React
frontend from `frontend/dist`, so the whole app lives behind one origin. The
`Dockerfile` builds the frontend then runs uvicorn. Planned hosting: Render
(Docker), a `map.` / dedicated subdomain, cross-linked from p3mai.com.

Note: on an ephemeral-disk host (Render free tier) `methodmap.db` resets on
restart — harmless, because the app re-seeds from the bundled JSON on boot. Any
**authoring-mode edits are stored only in that database**, so move to a
persistent disk or Postgres before relying on in-app edits surviving a redeploy.

## Data provenance

Entity names are corroborated from public sources. The 41 activities and their
codes are a best-effort reconstruction from prince2.wiki (CC-BY 4.0) and are
flagged "indicative" throughout — SME-verify against the licensed PRINCE2 manual
before any formal (audit / training / certification) use. Regenerate the seed
from the source spreadsheet with the extractor in project notes if the source
changes.
