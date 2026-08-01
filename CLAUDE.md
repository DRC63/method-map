# P3MAI Method Map — project notes for Claude

Interactive network-graph reference tool for project-management methods. v1 =
PRINCE2 7. Part of the P3MAI suite; same stack and conventions as the PMO Service
app (`../pmo-service`). Read `README.md` for the full picture; this file is the
quick orientation + the decisions that aren't obvious from the code.

## Stack & ports
- Backend: FastAPI + SQLAlchemy + SQLite (`methodmap.db`), WAL + synchronous=NORMAL.
- Frontend: React 19 + Vite, `react-force-graph-2d` for the graph.
- Dev ports: backend **8002**, frontend **5175** (registered in the working-dir
  `.claude/launch.json` as `method-map-backend` / `method-map-frontend`).
  PMO uses 8000/5173, p3m3 uses 8001/5174 — don't collide.

## Data model (framework-agnostic on purpose)
`frameworks` → `entities` → `relationships`.
- `entities.type` ∈ process | activity | role | practice | approach | product.
- Activities point at their process via `parent_id`. Everything else has no parent.
- `relationships` always go **activity → target** with a `code`
  (C/P/N for role/practice/approach, I/O/U/A for product) and a `confidence`.
- `confidence` ∈ confirmed | indicative. Activity rows + their codes are
  "indicative" (best-effort reconstruction); names are "confirmed".
- Processes carry lifecycle/timeline metadata: `lifecycle_level`
  (directing/managing/delivering), `lifecycle_phase`
  (pre-project/initiation/delivery/stage-boundary/final/throughout), `sequence`
  (left→right order), `repeats` (per delivery stage). Powers the Lifecycle view
  and the Explorer's Timeline layout.
- MSP (or any framework) is added purely as another seed JSON — no code changes.

## Lifecycle view (`GET /frameworks/{key}/lifecycle`, `pages/Lifecycle.jsx`)
The canonical PRINCE2 process model as a CSS-grid swimlane: 3 lanes (levels) ×
4 timeline columns (pre-project / initiation / delivery⟳ / final). DP is a
spanning bar across the directing lane; CS+SB stack in the managing/delivery
cell; MP sits in the delivering lane. Clicking a process shows its activities in
order; each activity (and the process) deep-links to the graph via `/?focus=<id>`
(Explorer reads the `focus` query param). A process's detail panel in the graph
also lists its child activities in sequence (processes have no relationship rows,
only `parent_id` containment — handled in `serialize_entity_detail`).

## Explorer layout (`components/GraphCanvas.jsx`, `theme/graphLayout.js`)
Two **fixed** layouts (no force/physics option), toggled in the control panel
(default **Matrix**). Both pin every node's `fx`/`fy`; GraphCanvas's positioning
effect picks the layout fn by `layout`. `cooldownTicks={0}` (pinned),
`autoPauseRedraw={false}` (highlight changes always repaint). Node size weighted
by **`direct_degree`** in both (sqrt scale `6.5 + √direct_degree·3.3`), computed
view-independently in `build_graph`. Colour-coded zone labels via
`onRenderFramePre` → `paintZones` (per-zone `scale` shrinks secondary labels).
Graph nodes carry `parent_id`, `sort_order`, `sequence`, `lifecycle_level`,
`lifecycle_phase` (all added to `GraphNode`/`build_graph`).
- **Matrix** (`computeStructuredLayout`) — hierarchy: processes top, activities
  beneath, products band below; roles left, practices right, approaches bottom.
- **Timeline** (`computeTimelineLayout`) — echoes the Project Lifecycle view:
  processes in three **swimlanes** (Directing / Managing / Delivering by
  `lifecycle_level`) laid left→right by `sequence`; activities stack in each
  process's time-column; roles / practices / approaches / products are static
  resource bands below. Plus a scrubber (`TimelineScrubber.jsx`), one stage per
  process. Each stage's highlight set = process + its activities + everything they
  link to; **spotlight** vs **cumulative** toggle + play button (`STAGE_MS`). Set
  computed in `Explorer.jsx`, passed to GraphCanvas as `timelineSet`, feeding the
  same dim/highlight machinery as hover/selection — nodes light up in place across
  the swimlanes + bands as you scrub.

## The graph builder (`app/graph.py`)
Given the selected entity-type layers it emits three link kinds:
- `contains`: process → activity (when both visible).
- `direct`: activity → target with its stored code (when activity layer visible).
- `derived`: undirected co-occurrence between two non-activity entities sharing an
  activity (a process counts as an implicit participant of its activities). This is
  what makes "hide Activities, show Roles↔Practices" meaningful.

## Seed (`app/seed.py`, `app/seed_data/*.json`)
- Auto-seeds an empty DB on boot (skipped under pytest). `python -m app.seed --force`
  wipes + reseeds. Loads every `*.json` in `seed_data/`.
- `prince2-7.json` was generated from
  `OneDrive/Documents/Methodologies/PRINCE2_MSP_Updated_Cross_Reference_Skeleton.xlsx`
  by `backend/scripts/extract_prince2.py`. Re-run that if the spreadsheet changes.
- Manual corrections/additions not in the source spreadsheet go in the
  `CORRECTIONS` list in `extract_prince2.py` (so they survive regeneration), then
  re-run the extractor + `python -m app.seed --force`. Schema changes need the
  local `methodmap.db` deleted first (create_all won't alter columns).
- Entities are referenced in the JSON by a composite `"type::name"` key.

## Auth (`app/security.py`)
Single shared password (`ADMIN_PASSWORD`, default `change-me`). Read = open;
writes require the `X-Admin-Password` header. Frontend stores it in localStorage
and gates authoring UI via `AdminContext`. Not real accounts — deliberate for v1.

## Deployment
- GitHub: `https://github.com/DRC63/method-map` (private, DRC63). Pushing to
  `main` **auto-deploys** (Render `autoDeploy: true`) — a push redeploys prod.
- **LIVE** on Render at `https://method-map.onrender.com` (Docker web service,
  Starter plan, region oregon) via the `render.yaml` Blueprint. Health check
  `/api/health`; `ADMIN_PASSWORD` is a dashboard secret (`sync: false`).
- Custom domain **prince2.p3mai.com** added in Render — live once a DNS
  `CNAME prince2 → method-map.onrender.com` exists at the p3mai.com DNS provider.
- Render disk is ephemeral → app auto-seeds on boot; authoring edits don't survive
  a redeploy (use a persistent disk / Postgres if they must).
- TODO: cross-link "Method Map" from the p3mai.com Services page (website side).

## Known environment gotchas
- The graph uses `requestAnimationFrame`; in a **non-displayed browser pane** the
  canvas won't paint and hit-testing/screenshots won't work. This is an
  environment limitation, not a bug — verify the graph in a real displayed browser.
- Project tree is under OneDrive: expect a ~2s write-commit tax on SQLite that
  pragmas can't remove (it's OneDrive's sync driver). WAL keeps reads snappy.

## Documentation (`docs/`)
Formal doc set organised like the *Microsoft Ecosystem – PMO Project*: numbered
Word docs each paired with a PowerPoint summary, a house style, and generated
diagrams. **DOC-01 Architecture & Design**, **DOC-02 User Manual**, **DOC-03
Operation Manual** (`.docx` + `_Summary.pptx`). The Office files are generated
from Python (`docs/_source/`: `docstyle.py`/`deckstyle.py` helpers + `gen_*.py`,
using python-docx / python-pptx / matplotlib) — edit the scripts and re-run to
rebuild. `docs/README.md` indexes them; `DOCUMENT_HOUSE_STYLE.md` is the
P3MAI-branded style. Word TOCs are auto-fields (press F9 to populate on first open).

## Tests
- Backend: `pytest` (isolated per-test SQLite DB; seeds the real framework).
- Frontend: `npm test` (Vitest). DetailPanel test mocks the api client.
