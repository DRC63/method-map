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
  (left→right order), `repeats` (per delivery stage). Powers the Lifecycle view.
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
Two layouts, toggled in the control panel (default **Matrix**):
- **Matrix** — a fixed positional hierarchy: processes across the top, each
  process's activities stacked beneath it, products in a band below, roles pinned
  left, practices right, management approaches along the bottom. Implemented by
  `computeStructuredLayout` assigning `fx`/`fy` to every node (d3-force pins them).
  Big, colour-coded, horizontal zone labels (one per entity type, in the clear
  band gaps) drawn via `onRenderFramePre` → `paintZones`. Needs `parent_id` +
  `sort_order` on graph nodes (added to `GraphNode`/`build_graph`).
  Node size in this layout is weighted by **`direct_degree`** — the count of real
  C/P/N/I/O/U/A relationships a node has (processes: child-activity count),
  computed view-independently in `build_graph` so it doesn't change with the
  layer/derived toggles. Sqrt scale (`5 + √direct_degree·2.9`).
- **Force** — original free-floating physics (strips `fx`/`fy`).

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
- Entities are referenced in the JSON by a composite `"type::name"` key.

## Auth (`app/security.py`)
Single shared password (`ADMIN_PASSWORD`, default `change-me`). Read = open;
writes require the `X-Admin-Password` header. Frontend stores it in localStorage
and gates authoring UI via `AdminContext`. Not real accounts — deliberate for v1.

## Known environment gotchas
- The graph uses `requestAnimationFrame`; in a **non-displayed browser pane** the
  canvas won't paint and hit-testing/screenshots won't work. This is an
  environment limitation, not a bug — verify the graph in a real displayed browser.
- Project tree is under OneDrive: expect a ~2s write-commit tax on SQLite that
  pragmas can't remove (it's OneDrive's sync driver). WAL keeps reads snappy.

## Tests
- Backend: `pytest` (isolated per-test SQLite DB; seeds the real framework).
- Frontend: `npm test` (Vitest). DetailPanel test mocks the api client.
