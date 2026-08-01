# P3MAI Method Map

An interactive reference tool that renders a project-management method as a
navigable network graph. v1 ships **PRINCE2 7**: 7 processes and 41 activities
cross-referenced to management team roles, practices, management approaches and
management products — the relationships from the PRINCE2/MSP cross-reference
skeleton, made explorable.

Built to match the PMO Service app (FastAPI + SQLite backend, React/Vite
frontend, single-origin Docker deploy); the app links back to the P3MAI website
(a link from the website to here is still to be added).

## What it does

Sidebar views: **Method Explorer**, **Project Lifecycle**, a **Guide**, and an
**Authoring & Admin** page.

### Method Explorer — the interdependency network graph
`react-force-graph-2d`, colour-coded nodes per entity type, with two **fixed
layouts** (toggle in the control panel):

- **Matrix** — a positional hierarchy: processes across the top, activities
  stacked beneath, products in a band below; roles pinned left, practices right,
  management approaches along the bottom, with big colour-coded zone labels.
- **Timeline** — echoes the Project Lifecycle: processes in three swimlanes
  (Directing / Managing / Delivering) laid left→right in lifecycle sequence,
  activities in each process's time-column, and roles / practices / approaches /
  products as static resource bands below. A **scrubber** (play/pause + slider +
  stage ticks) walks the lifecycle stage by stage, lighting up each stage's
  process, activities and everything they touch — in **spotlight** (current stage)
  or **cumulative** (everything so far) mode.

Shared across both layouts: toggle any entity **layer** on/off; **indirect
(co-occurrence) links** when activities are hidden (two elements connect when they
share an activity); **search**; node **size weighted by direct responsibilities**
(the real C/P/N/I/O/U/A relationship count); a prominent **selection highlight**
(click a node → gold halo + neighbour highlighting); and **confidence flags**
(dashed ring on "indicative" data).

### Project Lifecycle — the canonical PRINCE2 process model
Time runs left→right (Pre-project → Initiation → Delivery stages ⟳ → Final) across
the three swimlanes. Click a process to see its activities in sequence; jump
straight into the graph.

### Detail panel, authoring, exports
- **Detail panel** — click a node for every relationship, grouped and code-labelled
  (C/P/N for roles/practices/approaches; I/O/U/A for products), with the owning
  process for incoming links; a process lists its activities in sequence.
- **Authoring mode** — a single admin password unlocks add/edit/delete of entities
  and relationships (e.g. to populate a future MSP framework, or overtype an
  indicative code once SME-verified).
- **Exports** — graph as PNG, per-entity branded PDF summary, and the (optionally
  focused) cross-reference data as CSV / Excel.

## Architecture

- **Data model** is framework-agnostic: `frameworks` → `entities` (typed:
  process / activity / role / practice / approach / product; activities point at
  their process via `parent_id`) → `relationships` (from an activity to a target,
  with a code + confidence). Processes carry lifecycle metadata
  (`lifecycle_level`, `lifecycle_phase`, `sequence`, `repeats`) that powers the
  Project Lifecycle view and the Explorer's Timeline layout. MSP or any other
  framework drops in as another seed file with zero code changes.
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

**Live** on Render at **https://method-map.onrender.com** — a Docker web service
(Starter plan, Oregon) defined by `render.yaml` (Blueprint). Same single-origin
pattern as the PMO app: the backend serves the built React frontend from
`frontend/dist`, so the whole app lives behind one origin. `autoDeploy` is on, so
pushing to `main` redeploys. Health check: `/api/health`. `ADMIN_PASSWORD` is set
as a dashboard secret (`sync: false` in the blueprint).

Custom domain **prince2.p3mai.com** is attached in Render; it goes live once a DNS
`CNAME prince2 → method-map.onrender.com` is added at the p3mai.com DNS provider
(then Render auto-verifies + issues SSL).

Note: on Render's disk `methodmap.db` resets on each redeploy/restart — harmless,
because the app re-seeds from the bundled JSON on boot. Any **authoring-mode edits
are stored only in that database**, so move to a persistent disk or Postgres
before relying on in-app edits surviving a redeploy.

Still open: cross-link the "Method Map" from the p3mai.com Services page.

## Data provenance

Entity names are corroborated from public sources. The 41 activities and their
codes are a best-effort reconstruction from prince2.wiki (CC-BY 4.0) and are
flagged "indicative" throughout — SME-verify against the licensed PRINCE2 manual
before any formal (audit / training / certification) use. Regenerate the seed
from the source spreadsheet with the extractor in project notes if the source
changes.
