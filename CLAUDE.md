# P3MAI Method Map — project notes for Claude

Interactive network-graph reference tool for project-management methods. **Four
frameworks live** (2026-08-02), each its own Render deployment behind
`apps.p3mai.com/<slug>`: **PRINCE2 7** (`/prince2`), **MSP 5th ed** (`/msp`),
**SAFe 6.0 Essential** (`/safe`), **PMBOK 6th ed** (`/pmbok`). Part of the P3MAI
suite; same stack and conventions as the PMO Service app (`../pmo-service`). Read
`README.md` for the full picture; this file is the quick orientation + the
decisions that aren't obvious from the code.

## Stack & ports
- Backend: FastAPI + SQLAlchemy + SQLite (`methodmap.db`), WAL + synchronous=NORMAL.
- Frontend: React 19 + Vite, `react-force-graph-2d` for the graph.
- Dev ports: backend **8002**, frontend **5175** (registered in the working-dir
  `.claude/launch.json` as `method-map-backend` / `method-map-frontend`).
  PMO uses 8000/5173, p3m3 uses 8001/5174 — don't collide.

## Framework config (per-framework definition — the generalization)
Each framework carries a `config` JSON (on the `frameworks` row, seeded from the
JSON's `framework.config`) that makes the whole app framework-agnostic:
- `types`: ordered `[{key,label,color,kind,zone,code_group,label_below?}]`. **kind**:
  `container` (owns children via parent_id) · `hub` (carries the coded relationships) ·
  `node` (a relationship target). **zone**: Matrix placement (`top`/`center`/`below`/
  `left`/`right`/`bottom`). `label_below: true` on a `below`-zone node type puts its
  Matrix zone heading UNDER the band (PMBOK Tools & Techniques). The graph builder
  derives container/hub from `kind` (no hardcoded process/activity); the frontend
  derives colours/labels/layout from this.
- `codes`: `{group:{code:label}}` (PRINCE2 role → C/P/N, product → I/O/U/A; PMBOK
  artifact → I/O, tool → T; etc.). Unknown codes auto-get a legend colour.
- `lanes`: Timeline swimlanes `[{key,label}]`; `phases`: `[{key,label,column?,header?}]`.
- `lifecycle_layer`: `"container"` (default) or **`"hub"`** — which layer fills the
  Lifecycle/Timeline swimlane cells. PMBOK sets `"hub"` so the **processes** grid into
  their own (lane=KA, phase=Process-Group) cell (the 5×10 matrix), instead of the
  container filling cells with child hubs beneath. Honoured by `get_lifecycle`
  (backend), `Lifecycle.jsx` and `TimelineSwimlane.jsx` (both check
  `theme.lifecycleLayer`); `timeline.heading`/`intro`/`start_label`/`end_label` in
  config override the Lifecycle page wording (cyclic frameworks, PMBOK).
Frontend builds a theme from it via `makeFrameworkTheme` (theme/theme.js). **A new
framework = a new seed JSON with its own config; no code change** for the graph/
Explorer/Lifecycle/swimlane (PMBOK's hub-grid was the one small, opt-in exception).
The **only** hand-written per-framework code is `pages/Guide.jsx` →
`FRAMEWORK_PROSE[key]` = `{modelName, accuracy, related}`; the `related` cross-links
are now generated from a **data-driven `APPS` list + `relatedNote()` helper** →
**4-way**, and a new framework is a **ONE-line add** to `APPS` (no longer "edit every
entry"). NOTE those links are template literals (`https://apps.p3mai.com/${slug}/`) →
grepping a prod bundle for the concatenated URL FALSE-NEGATIVES (check `holds side by
side` / `PMI process standard`). Env `FRAMEWORK_KEY` makes a deployment seed+default
to one framework (`/api/meta` `default_framework`) — how all four deploy separately.

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
- MSP (or any framework) is added purely as another seed JSON — no code changes
  (except the Guide's per-framework prose + `related` cross-links; see Framework config above).

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
- **Matrix** (`computeStructuredLayout`) — hierarchy: container top, hubs beneath,
  `below`-zone bands under them; `left`/`right`/`bottom` node types flank. A
  `below`-zone type with `label_below:true` draws its heading UNDER the band (PMBOK
  Tools & Techniques sits under Inputs & Outputs so the spine is centred, not
  lopsided). PMBOK = Knowledge-Areas top, Processes, then Inputs&Outputs + Tools bands.
- **Timeline** (`components/TimelineSwimlane.jsx`) — a **CSS-grid swimlane**, NOT
  the force-graph (rewritten 2026-08-02; it used to be `computeTimelineLayout` on
  the canvas). Rows = lanes (`theme.lanes`, e.g. Directing/Managing/Delivering or
  Sponsoring/Managing/Delivering), columns = stage phases (`theme.phases` where
  `column`, header `Delivery ⟳` etc.); each process sits in its `(lane, phase)`
  cell (non-column phases like `throughout`/`stage-boundary` fold into the delivery
  column) with its activities as dots beneath; node-type layers (`theme.nodeTypes`)
  render as static **resource bands** below. Fully framework-driven — **verified
  live on all four** (SAFe has only 2 lanes and uses `event` as the container).
  **PMBOK hub-grid (2026-08-02):** when `theme.lifecycleLayer === 'hub'` the swimlane
  fills cells with the **hub** layer (the 49 processes) by their own
  `lifecycle_level`/`lifecycle_phase` — NOT the container — with no child dots; this
  is what renders the 10 KA × 5 Process-Group matrix. (Without this fix the Timeline
  was blank for PMBOK: KAs-as-containers have no lifecycle_level/phase, so every cell
  was empty.) `Lifecycle.jsx` also generates a lane palette (HSL by index) for
  frameworks with >3 lanes. Clicking any process/activity/resource → `onSelectNode`
  → detail panel. **Scrubber (`TimelineScrubber.jsx`) retained**, one stage per process:
  `timelineSet` (computed in `Explorer.jsx`, spotlight = current stage's ids,
  cumulative = 0..i) is passed to the swimlane, which dims non-members (`.tl-dim`)
  and rings the selection (`.tl-sel`). Key UX: a `timelineTouched` flag means the
  swimlane shows **every stage at full strength until the scrubber is used**, so it
  reads as a full swimlane on entry, then spotlights on interaction. A **Reset button**
  (gold pill in the scrubber, `.timeline-reset`, `onReset` → Explorer clears
  `selectedId` + `timelineIndex=0` + `playing=false` + `timelineTouched=false`) clears
  the node selection AND the scrub spotlight back to the full view. NOTE the PNG
  export (`graphRef.exportPng`) only works in Matrix — it's a no-op in Timeline
  (there's no canvas); CSV/Excel still work. A framework-driven **legend**
  (`.tl-legend`, above the grid) shows a colour swatch + label per node type
  (from `theme.colorOf`/`labelOf`) plus a lit/faded scrubber hint. Styles are the
  `.tl-*` classes in `theme/theme.css`. **Layout:** in Timeline mode `Explorer.jsx`
  adds `is-timeline` to `.graph-stage`, making it a **flex column** so the scrolling
  `.tl-swim` sits above an **in-flow** `.timeline-bar` (the scrubber) — do NOT put the
  scrubber back to `position:absolute`, that floated it OVER the swimlane and hid the
  bottom resource bands. Matrix keeps `display:block` (canvas children are absolute).
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
- **Mobile / responsive (`@media (max-width: 820px)` in theme.css)** — the base
  layout is a fixed desktop 3-pane (sidebar + control panel + graph + detail) and
  `.app-shell { overflow:hidden }` used to clip the graph off-screen on phones. On
  small screens: `.app-shell` becomes a scrolling flex **column**, the **sidebar** is
  a top bar (horizontal nav), `.graph-stage` gets full width + `min-height:72vh`, the
  **control panel is a left slide-in drawer** (`.explorer.controls-open` toggled by
  the `.mobile-controls-toggle` button in `Explorer.jsx`, with a `.mobile-drawer-
  backdrop`), and the **detail panel is a full-screen overlay**. Desktop is untouched.
  The drawer uses NO transition on purpose (the transform-transition doesn't progress
  in the non-compositing preview pane; snapping is reliable everywhere).

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
- **MSP / SAFe / PMBOK have NO source spreadsheet** — each is an inline builder:
  `scripts/build_msp.py` (msp-5), `build_safe.py` (safe-essential), `build_pmbok.py`
  (pmbok-6). Framework vocab is confirmed; the activity/ITTO breakdown + every
  cross-ref mark are an **indicative** reconstruction (SME-verify). PMBOK = 187 ent /
  400 marks (10 KAs, 49 processes, 66 artifacts, 62 tools); the PG×KA grid + process
  names are confirmed, ITTOs curated-indicative. Trademark disclaimers in each
  framework `description` (AXELOS/PeopleCert, Scaled Agile, PMI).
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
- GitHub: `https://github.com/DRC63/method-map` (private, DRC63). Pushing to `main`
  **auto-deploys ALL FOUR services** (they share the repo) — one `render.yaml`
  Blueprint, one Docker service **per framework**, differing only in `FRAMEWORK_KEY`
  + the `APP_BASE` build arg (`/prince2/`, `/msp/`, `/safe/`, `/pmbok/`). Each Starter,
  oregon; health `/api/health`; `ADMIN_PASSWORD` a per-service dashboard secret
  (`sync:false`). Services: `method-map` (prince2), `msp-method-map`, `safe-method-map`,
  `pmbok-method-map`. **Adding a framework = new render.yaml service block → push →
  sync the Blueprint in Render + set its ADMIN_PASSWORD.**
- **Front door** `apps.p3mai.com` (separate repo **DRC63/apps-gateway**, a Node reverse
  proxy) routes `/prince2 /msp /safe /pmbok` (+ /pmo /p3m3) to each service — one line
  in its `ORIGINS`. Replaced the old per-app subdomains (no `prince2.p3mai.com`).
- **Architecture decision (Douglas, 2026-08-02): keep apps SEPARATE** (one service
  each, "Option 1"). A single-service + in-app framework switcher ("Option C", ~2 days,
  $0 extra — rendering is already config-driven, only the `list[0]` selection is
  hardcoded) was sketched but **declined**. Free-tier per-service also available.
- Render disk is ephemeral → auto-seeds its `FRAMEWORK_KEY` on boot; authoring edits
  don't survive a redeploy (use a persistent disk / Postgres if they must).
- **Website**: p3mai.com Services page (Project Management card) has PRINCE2 + SAFe +
  PMBOK buttons, Programme card has MSP — env-aware in `business-website/script.js`
  (localhost sentinel → `apps.p3mai.com/<slug>`). Site is on **Rise** (NOT git-auto-
  deployed) → publishing a button = upload `services.html`+`script.js` to Rise + bump
  `script.js?v=` to bust the edge cache.

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
- **CI**: `.github/workflows/ci.yml` runs both on push/PR to main (Python 3.12 / Node 20);
  `dependabot.yml` raises weekly update PRs. NOTE: CI reports status but does not block
  Render's auto-deploy unless "Wait for CI to pass" is enabled per service.

## Recent additions (2026-08-03/04) — not to be mistaken as missing
- **Worked-example PDFs** in the detail panel: config-driven `framework.config.examples`
  (entity name → bundled `frontend/public/examples/<fw>/*.pdf`) drives a generic "View
  worked example" button in `EntityDetailPanel.jsx`. All 4 frameworks wired.
- **Auth fails closed** (`app/security.py`): no default password — writes are rejected
  unless `ADMIN_PASSWORD` is set (an unconfigured service is read-only, not wide open).
- **Optional Sentry** (`app/observability.py`): `init_sentry()` is inert (lazy import)
  unless `SENTRY_DSN` is set.
- **Security headers + uptime**: applied at the gateway (`../apps-gateway/server.js`) and
  a scheduled uptime workflow lives in the gateway repo — not here.
- Full history for these is in the auto-memory `project_method_map`.
