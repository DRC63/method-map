"""Generate 01_Architecture_and_Design.docx for the P3MAI Method Map."""
import os
import docstyle as ds

OUT = os.path.join(os.path.dirname(__file__), "..", "01_Architecture_and_Design.docx")
ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
VERSION = "v1.0"
DATE = "1 August 2026"

doc = ds.new_doc()
ds.footer(doc, "OFFICIAL", VERSION)
ds.title_page(doc, "DOC-01", "Architecture & Design",
              "Technical design of the P3MAI Method Map",
              VERSION, DATE, "Douglas Colvin, P3MAI", "OFFICIAL")
ds.doc_control(doc, [[VERSION, "2026-08-01", "Douglas Colvin", "Initial issue"]])
ds.add_toc(doc)

# 1. Executive summary
ds.heading(doc, "1.  Executive summary", 1)
ds.para(doc, "The **P3MAI Method Map** is an interactive web application that renders a "
        "project-management method as a navigable network graph. Version 1 covers **PRINCE2 7** — "
        "its 7 processes and 41 activities cross-referenced to the management team roles, practices, "
        "management approaches and management products they use, produce and are governed by.")
ds.para(doc, "It is built as a single-origin web application: a **FastAPI** backend serving a "
        "**React** single-page front end, backed by a **SQLite** database that auto-seeds from a "
        "bundled data file. The data model is deliberately framework-agnostic, so MSP or any other "
        "method can be added as a data file without code changes. The application is deployed as a "
        "Docker container on Render and is reachable at **method-map.onrender.com** "
        "(custom domain **prince2.p3mai.com** pending DNS).")
ds.para(doc, "This document describes the system architecture, data model, backend and front-end "
        "design, the graph and layout algorithms, security, deployment, and the key design decisions.")

# 2. Introduction
ds.heading(doc, "2.  Introduction", 1)
ds.heading(doc, "2.1  Purpose", 2)
ds.para(doc, "To provide the authoritative technical reference for the Method Map — enough for a "
        "developer to understand, maintain, extend and re-deploy the system.")
ds.heading(doc, "2.2  Scope", 2)
ds.para(doc, "Covers the application as built: backend, front end, data, deployment and security. "
        "Operational procedures are in the **Operation Manual (DOC-03)**; end-user guidance is in the "
        "**User Manual (DOC-02)**.")
ds.heading(doc, "2.3  Audience", 2)
ds.para(doc, "Developers and technical reviewers. Assumes familiarity with Python, JavaScript/React "
        "and containers, but not with the PRINCE2 method itself (see the glossary).")
ds.heading(doc, "2.4  Definitions", 2)
ds.table(doc, ["Term", "Meaning"], [
    ["Entity", "A typed node in the graph — a process, activity, role, practice, management approach or product."],
    ["Relationship", "A coded edge from an activity to a target entity."],
    ["Code", "C/P/N for roles, practices and approaches; I/O/U/A for products (see §5.3)."],
    ["Framework", "A whole method (e.g. PRINCE2 7). The model supports several side by side."],
    ["SPA", "Single-page application — the React front end."],
], col_widths=[3.0, 12.5])

# 3. System overview
ds.heading(doc, "3.  System overview", 1)
ds.para(doc, "The Method Map turns the PRINCE2 cross-reference — normally a dense spreadsheet grid — "
        "into an explorable network. Users can:")
ds.bullet(doc, "explore the interdependencies as a graph in two fixed layouts (**Matrix** and **Timeline**);")
ds.bullet(doc, "walk the project **lifecycle** stage by stage and watch each stage's elements light up;")
ds.bullet(doc, "select any element to see every relationship it takes part in, with the standard codes;")
ds.bullet(doc, "export views as PNG, a branded PDF, or CSV/Excel; and")
ds.bullet(doc, "(for authorised editors) correct or extend the underlying data in place.")

# 4. Technology stack
ds.heading(doc, "4.  Technology stack", 1)
ds.table(doc, ["Layer", "Technology", "Role"], [
    ["Backend framework", "FastAPI (Python 3.12)", "REST API and SPA host"],
    ["ORM / DB", "SQLAlchemy + SQLite", "Persistence (WAL + synchronous=NORMAL)"],
    ["Validation", "Pydantic", "Request/response schemas"],
    ["Server", "uvicorn", "ASGI server"],
    ["Exports", "openpyxl, reportlab", "Excel/CSV and branded PDF generation"],
    ["Front-end framework", "React 19 + Vite", "Single-page application"],
    ["Graph", "react-force-graph-2d", "Canvas network rendering"],
    ["Routing", "react-router", "Client-side views"],
    ["Packaging", "Docker (multi-stage)", "Single-image build & deploy"],
    ["Hosting", "Render (Docker web service)", "Production runtime"],
], col_widths=[3.6, 4.4, 7.5])
ds.para(doc, "The stack deliberately mirrors the sibling **PMO Service** app so the two share "
        "conventions, brand and deployment pattern.")

# 5. Solution architecture
ds.heading(doc, "5.  Solution architecture", 1)
ds.para(doc, "The application runs as a **single origin**: in production the FastAPI backend serves "
        "the pre-built React bundle from `frontend/dist`, and the same process exposes the `/api/*` "
        "routes. There is no separate API host, so there are no cross-origin concerns in production.")
ds.figure(doc, os.path.join(ASSETS, "arch_deployment.png"),
          "Figure 1 — Deployment architecture (single-origin Docker service on Render).")
ds.heading(doc, "5.1  Components", 2)
ds.table(doc, ["Component", "Responsibility"], [
    ["FastAPI app (app/main.py)", "Wires routers, CORS, first-boot seeding, and the SPA fallback."],
    ["Routers", "meta, frameworks, entities, relationships — the REST surface."],
    ["Graph builder (app/graph.py)", "Turns stored entities/relationships into nodes + links for a view."],
    ["Serializers / CRUD", "ORM ↔ Pydantic conversion and database operations."],
    ["Exports (app/exports.py)", "CSV, XLSX and per-entity PDF generation."],
    ["Seed (app/seed.py)", "Loads the bundled JSON into the database on first boot."],
    ["React SPA", "Explorer, Lifecycle, Guide and Authoring views."],
], col_widths=[4.8, 10.7])
ds.callout(doc, "note", "Single-origin, single-image",
           ["The multi-stage Dockerfile builds the React bundle in a Node stage, then copies it into "
            "the Python image. One container serves both the API and the UI — nothing else to run."])

# Data model
ds.heading(doc, "6.  Data model", 1)
ds.para(doc, "The model is framework-agnostic on purpose. A **framework** owns a set of **entities**, "
        "and **relationships** connect them. Adding MSP means adding a data file — no schema change.")
ds.figure(doc, os.path.join(ASSETS, "arch_datamodel.png"),
          "Figure 2 — Data model: framework → entities → relationships, with entity types and codes.")
ds.heading(doc, "6.1  Entities", 2)
ds.table(doc, ["Field", "Notes"], [
    ["type", "process | activity | role | practice | approach | product"],
    ["name, code", "Display name; short code (e.g. SU, DP) where one exists"],
    ["parent_id", "Activity → its owning process (null for everything else)"],
    ["subgroup", "Products only: baseline | log | report"],
    ["confidence", "confirmed | indicative (activity-level data is a best-effort reconstruction)"],
    ["lifecycle_level", "Processes: directing | managing | delivering (swimlane)"],
    ["lifecycle_phase", "Processes: pre-project / initiation / delivery / stage-boundary / final / throughout"],
    ["sequence", "Processes: left→right lifecycle order (SU=1 … CP=7)"],
    ["sort_order", "Stable ordering within a type"],
], col_widths=[3.4, 12.1])
ds.heading(doc, "6.2  Relationships", 2)
ds.para(doc, "Every relationship goes **from an activity to a target** (role/practice/approach/product) "
        "and carries a **code** and a **confidence**. Processes are not endpoints of relationships — "
        "they own activities through `parent_id`.")
ds.heading(doc, "6.3  The codes", 2)
ds.table(doc, ["Applies to", "Codes"], [
    ["Roles, practices, management approaches", "C = Responsible · P = Participates · N = Assists"],
    ["Management products", "I = Input · O = Output · U = Update · A = Authorise"],
], col_widths=[6.5, 9.0])
ds.callout(doc, "tip", "Why activity-centric?",
           ["Storing every relationship as activity→target keeps the data honest and small (one row per "
            "real cross-reference mark). All higher-level connections — role↔product, process↔practice — "
            "are derived from these at query time, so nothing is duplicated or can drift out of sync."])

# 7. Backend design
ds.heading(doc, "7.  Backend design", 1)
ds.heading(doc, "7.1  API surface", 2)
ds.table(doc, ["Method & path", "Purpose", "Auth"], [
    ["GET /api/health", "Liveness probe", "open"],
    ["GET /api/meta", "Entity types, code labels, subgroups", "open"],
    ["POST /api/auth/verify", "Check the admin password", "open"],
    ["GET /api/frameworks", "List frameworks + entity counts", "open"],
    ["GET /api/frameworks/{key}/entities", "List entities (filter by type/search)", "open"],
    ["GET /api/frameworks/{key}/relationships", "List raw relationships", "open"],
    ["GET /api/frameworks/{key}/graph", "Build nodes + links for a view", "open"],
    ["GET /api/frameworks/{key}/lifecycle", "Processes in sequence with activities", "open"],
    ["GET /api/entities/{id}", "Entity detail with grouped relationships", "open"],
    ["GET …/export.csv, /export.xlsx", "Cross-reference data export", "open"],
    ["GET …/entities/{id}/report.pdf", "Branded per-entity PDF", "open"],
    ["POST/PUT/DELETE /api/entities", "Create/edit/delete entities", "admin"],
    ["POST/PUT/DELETE /api/relationships", "Create/edit/delete relationships", "admin"],
], col_widths=[5.6, 6.9, 3.0])
ds.heading(doc, "7.2  The graph builder", 2)
ds.para(doc, "`build_graph()` turns the stored data into the nodes and links a view needs, given the "
        "selected entity-type layers and whether indirect links are wanted. It emits three link kinds:")
ds.bullet(doc, "**contains** — process → activity (structural, when both layers are visible);")
ds.bullet(doc, "**direct** — activity → target, carrying the stored code (when the activity layer is visible);")
ds.bullet(doc, "**derived** — an undirected co-occurrence link between two non-activity entities that "
          "share an activity (a process counts as an implicit participant of its activities).")
ds.figure(doc, os.path.join(ASSETS, "arch_graph_model.png"),
          "Figure 3 — The three link kinds the graph builder produces.")
ds.para(doc, "Derived links are what make the \"hide Activities, show Roles↔Practices\" view meaningful — "
        "the connection runs *through* the shared activities.")
ds.heading(doc, "7.3  Node weighting", 2)
ds.para(doc, "Each node carries two degree measures:")
ds.bullet(doc, "**degree** — total edges touching it in the current view (view-dependent); used by the "
          "force sizing historically;")
ds.bullet(doc, "**direct_degree** — the count of real C/P/N/I/O/U/A relationships the entity takes part "
          "in, computed view-independently (for processes: how many activities they contain). This is "
          "the stable \"direct responsibilities\" measure that drives node size in the fixed layouts "
          "(sqrt scale, so area ∝ count).")
ds.heading(doc, "7.4  Exports & seeding", 2)
ds.para(doc, "CSV/XLSX flatten the cross-reference (optionally focused on one entity); the PDF is a "
        "branded per-entity relationship summary via reportlab. Seeding loads every `*.json` file in "
        "`app/seed_data/` on first boot; it is idempotent and skipped under tests.")

# 8. Front-end design
ds.heading(doc, "8.  Front-end design", 1)
ds.heading(doc, "8.1  Views", 2)
ds.table(doc, ["View", "What it does"], [
    ["Method Explorer", "The network graph, in Matrix or Timeline layout, with layers/search/detail."],
    ["Project Lifecycle", "The canonical PRINCE2 process model as a swimlane; activities in sequence."],
    ["Guide", "Plain-English explanation of the layers, codes and confidence flags."],
    ["Authoring & Admin", "Password-gated editing of entities and relationships."],
], col_widths=[3.8, 11.7])
ds.heading(doc, "8.2  The two layouts", 2)
ds.para(doc, "Both layouts pin every node's position (`fx`/`fy`) so d3-force holds them in place; there "
        "is no free-floating physics option. Colour-coded zone labels are drawn behind the nodes.")
ds.bullet(doc, "**Matrix** — a fixed hierarchy: processes across the top, activities stacked beneath, "
          "products in a band below; roles pinned left, practices right, management approaches along the bottom.")
ds.bullet(doc, "**Timeline** — echoes the Lifecycle view: processes in three swimlanes (Directing / "
          "Managing / Delivering) laid left→right by sequence; activities in each process's time-column; "
          "roles/practices/approaches/products as static resource bands below. A scrubber walks the "
          "lifecycle, lighting up each stage's sub-graph (spotlight or cumulative), with a play button.")
ds.heading(doc, "8.3  Interaction", 2)
ds.para(doc, "Selecting a node enlarges it with a gold glow halo and highlights its neighbourhood; the "
        "detail panel lists every relationship. Hovering highlights a node's neighbours. Search flags "
        "matches. Deep links (`/?focus=<id>`) select a node on arrival — used by the Lifecycle view.")

# 9. Data provenance
ds.heading(doc, "9.  Data provenance & seeding", 1)
ds.para(doc, "The PRINCE2 dataset (`app/seed_data/prince2-7.json`, 91 entities / 206 relationships) "
        "was generated from the PRINCE2/MSP cross-reference spreadsheet by "
        "`backend/scripts/extract_prince2.py`. Manual corrections not present in the source spreadsheet "
        "live in a `CORRECTIONS` list in that extractor, so they survive regeneration.")
ds.callout(doc, "pitfall", "Indicative vs confirmed",
           ["Process, role, practice, approach and product **names** are corroborated from public "
            "sources and marked *confirmed*. The 41 activities and their codes are a best-effort "
            "reconstruction (prince2.wiki, CC-BY 4.0) and are marked *indicative* (shown with a dashed "
            "ring). SME-verify against the licensed PRINCE2 manual before any formal use."])

# 10. Security
ds.heading(doc, "10.  Security & access control", 1)
ds.para(doc, "Read access is fully open — the app is a public reference tool with no personal data. "
        "Write operations (authoring) require a single shared password sent as an `X-Admin-Password` "
        "header and checked against the `ADMIN_PASSWORD` environment variable. This is a deliberate, "
        "lightweight gate — enough to stop casual edits, not a full account system.")
ds.callout(doc, "note", "Security posture",
           ["No authentication for reads (by design). Single admin password for writes. Single origin, "
            "so no third-party data egress. Revisit if the app ever holds sensitive or personal data."])

# 11. Deployment
ds.heading(doc, "11.  Deployment architecture", 1)
ds.para(doc, "Deployed via a Render **Blueprint** (`render.yaml`): a Docker web service, Starter plan, "
        "Oregon region, health check `/api/health`, `ADMIN_PASSWORD` as a dashboard secret. Pushing to "
        "the `main` branch of the GitHub repo auto-deploys. The database re-seeds on every boot, so a "
        "fresh or restarted container comes up populated.")
ds.table(doc, ["Aspect", "Value"], [
    ["Repository", "github.com/DRC63/method-map (private)"],
    ["Platform", "Render — Docker web service, Starter, Oregon"],
    ["URL", "method-map.onrender.com (prince2.p3mai.com pending DNS)"],
    ["Auto-deploy", "On push to main"],
    ["Persistence", "Ephemeral disk — DB resets on redeploy; auto-seeds"],
], col_widths=[3.6, 11.9])
ds.callout(doc, "pitfall", "Ephemeral database",
           ["Render's disk is ephemeral, so authoring-mode edits do not survive a redeploy. Move to a "
            "persistent disk or Postgres before relying on in-app edits."])

# 12. Design decisions
ds.heading(doc, "12.  Key design decisions", 1)
ds.table(doc, ["Decision", "Rationale"], [
    ["Framework-agnostic data model", "MSP and other methods drop in as data files, no code change."],
    ["Activity-centric relationships", "One row per real cross-reference mark; higher links derived, never duplicated."],
    ["Self-contained JSON seed + auto-seed", "Deploy is independent of the source spreadsheet; ephemeral hosts self-populate."],
    ["Two fixed layouts (no physics)", "Positional meaning (hierarchy / lifecycle) reads better than an organic blob."],
    ["direct_degree node weighting", "Size reflects real responsibilities, stable across layer/derived toggles."],
    ["Single admin password", "Lightweight edit gate appropriate to an open, non-sensitive reference tool."],
], col_widths=[5.2, 10.3])

# 13. Non-functional
ds.heading(doc, "13.  Non-functional considerations", 1)
ds.bullet(doc, "**Performance** — the dataset is small (~90 nodes); the graph renders on the client. "
          "SQLite runs WAL + synchronous=NORMAL. Locally the project sits under OneDrive, which adds a "
          "sync write latency that pragmas cannot remove — irrelevant in the deployed container.")
ds.bullet(doc, "**Scalability** — comfortably handles multiple frameworks; the graph endpoint is O(edges).")
ds.bullet(doc, "**Portability** — one Docker image; runs anywhere that runs containers.")
ds.bullet(doc, "**Extensibility** — MSP-ready model; new export formats and layouts slot into existing seams.")

# 14. Roadmap
ds.heading(doc, "14.  Roadmap", 1)
ds.bullet(doc, "Populate and enable **MSP 5th Edition** as a second framework.")
ds.bullet(doc, "Persistent storage (disk or Postgres) so authoring edits survive redeploys.")
ds.bullet(doc, "Saved per-engagement **tailored views** (schema already anticipates this).")
ds.bullet(doc, "Optional user accounts if the tool ever holds sensitive data.")

# Appendix
ds.heading(doc, "Appendix A — Repository layout", 1)
ds.code_block(doc,
              "method-map/\n"
              "  backend/app/        FastAPI app (main, models, schemas, crud, graph,\n"
              "                      serializers, exports, seed, security, routers/)\n"
              "  backend/app/seed_data/prince2-7.json   bundled dataset\n"
              "  backend/scripts/extract_prince2.py     spreadsheet → seed extractor\n"
              "  frontend/src/       React app (pages/, components/, theme/, api/)\n"
              "  Dockerfile          multi-stage build\n"
              "  render.yaml         Render Blueprint\n"
              "  docs/               this documentation set")

doc.save(OUT)
print("wrote", os.path.abspath(OUT), os.path.getsize(OUT), "bytes")
