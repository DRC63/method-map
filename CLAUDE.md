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

## Framework config (per-framework definition — the generalization)
Each framework carries a `config` JSON (on the `frameworks` row, seeded from the
JSON's `framework.config`) that makes the whole app framework-agnostic:
- `types`: ordered `[{key,label,color,kind,zone,code_group}]`. **kind**: `container`
  (owns children via parent_id) · `hub` (carries the coded relationships) · `node`
  (a relationship target). **zone**: Matrix placement (`top`/`center`/`below`/`left`/
  `right`/`bottom`). The graph builder derives container/hub from `kind` (no
  hardcoded process/activity); the frontend derives colours/labels/layout from this.
- `codes`: `{group:{code:label}}` (role → C/P/N, product → I/O/U/A).
- `lanes`: Timeline swimlanes `[{key,label}]`; `phases`: `[{key,label,column?,header?}]`.
Frontend builds a theme from it via `makeFrameworkTheme` (theme/theme.js), threaded
through GraphCanvas/ControlPanel/EntityDetailPanel and the layout fns (graphLayout.js,
now zone/lane-driven). **A new framework (MSP) = a new seed JSON with its own config;
no code change.** Env `FRAMEWORK_KEY` makes a deployment seed+default to one framework
(exposed via `/api/meta` `default_framework`) — this is how PRINCE2 and MSP deploy
separately from one codebase.

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

## Explorer layout (`components/GraphCanvas.jsx`, `components/TimelineSwimlane.jsx`, `theme/graphLayout.js`)
Two layouts, toggled in the control panel (default **Matrix**). **Matrix is the
force-graph** (`GraphCanvas`); **Timeline is a DOM swimlane** (`TimelineSwimlane`,
NOT the force-graph) — `Explorer.jsx` renders one or the other by `layout`.
GraphCanvas pins every node's `fx`/`fy`; its positioning effect picks the layout
fn by `layout`. `cooldownTicks={0}` (pinned),
`autoPauseRedraw={false}` (highlight changes always repaint). Node size weighted
by **`direct_degree`** in both (sqrt scale `6.5 + √direct_degree·3.3`), computed
view-independently in `build_graph`. Colour-coded zone labels via
`onRenderFramePre` → `paintZones` (per-zone `scale` shrinks secondary labels).
Graph nodes carry `parent_id`, `sort_order`, `sequence`, `lifecycle_level`,
`lifecycle_phase` (all added to `GraphNode`/`build_graph`).
- **Matrix** (`computeStructuredLayout`) — hierarchy: processes top, activities
  beneath, products band below; roles left, practices right, approaches bottom.
- **Timeline** (`components/TimelineSwimlane.jsx`) — a **CSS-grid swimlane**, NOT
  the force-graph (rewritten 2026-08-02; it used to be `computeTimelineLayout` on
  the canvas). Rows = lanes (`theme.lanes`, e.g. Directing/Managing/Delivering or
  Sponsoring/Managing/Delivering), columns = stage phases (`theme.phases` where
  `column`, header `Delivery ⟳` etc.); each process sits in its `(lane, phase)`
  cell (non-column phases like `throughout`/`stage-boundary` fold into the delivery
  column) with its activities as dots beneath; node-type layers (`theme.nodeTypes`)
  render as static **resource bands** below. Fully framework-driven (works for
  PRINCE2 + MSP). Clicking any process/activity/resource → `onSelectNode` → detail
  panel. **Scrubber (`TimelineScrubber.jsx`) retained**, one stage per process:
  `timelineSet` (computed in `Explorer.jsx`, spotlight = current stage's ids,
  cumulative = 0..i) is passed to the swimlane, which dims non-members (`.tl-dim`)
  and rings the selection (`.tl-sel`). Key UX: a `timelineTouched` flag means the
  swimlane shows **every stage at full strength until the scrubber is used**, so it
  reads as a full swimlane on entry, then spotlights on interaction. NOTE the PNG
  export (`graphRef.exportPng`) only works in Matrix — it's a no-op in Timeline
  (there's no canvas); CSV/Excel still work. Styles are the `.tl-*` classes in
  `theme/theme.css`.
- **Search spotlights matches** — the Search box folds `searchMatches` into
  GraphCanvas's effective `highlightSet` (precedence hover → timeline → search →
  selection), so an active query dims every non-match (nodes **and** links) and the
  matches stay lit. (Before, it only drew a faint gold ring → looked broken.)
- **Control-panel blurbs are framework-driven** — the Timeline/Matrix description
  text in `ControlPanel.jsx` derives lane names from `theme.lanes` and layer
  positions from the config **zones** (`container` top / `hub` below / `below` under
  / `left`/`right`/`bottom`). The PRINCE2 lane/layer names in the two bullets above
  are just the PRINCE2 case; MSP shows Sponsoring/Managing/Delivering + Roles/Themes/
  Principles. Don't re-hardcode PRINCE2 terms here.

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
  In the Claude Code session specifically there is **no way to screen-capture the
  force-graph**: the in-app pane never composites it, `claude-in-chrome` blocks both
  `localhost` and the live domain, and the app's PNG export needs a painted canvas.
  To "show" the graph (e.g. the Timeline swimlanes), build a **faithful SVG/HTML
  schematic from the live API data** and `SendUserFile` it. Non-canvas DOM (control
  panel, blurbs, search input, Guide, sidebar) IS readable via the pane's
  `javascript_tool`/`read_page`, so verify those there.
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
