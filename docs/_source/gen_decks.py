"""Generate the three PowerPoint summary decks for the Method Map docs."""
import os
from deckstyle import Deck, NAVY, GOLDD, GREEN, RED, PURPLE, TEXT

HERE = os.path.dirname(__file__)
DOCS = os.path.join(HERE, "..")
A = lambda n: os.path.join(DOCS, "assets", n)


# ============ 01 — Architecture & Design ============
d = Deck("DOC-01", "OFFICIAL")
d.title_slide("Architecture & Design", "Technical design of the P3MAI Method Map — summary")
d.bullets("What it is", [
    "Four methods as interactive network graphs: PRINCE2 7, MSP 5th ed, SAFe 6.0 Essential, PMBOK 6th ed.",
    "Each cross-references its activities/processes to the roles, artefacts, tools and principles around them.",
    "Single-origin web app; config-driven, framework-agnostic model — a new method is (almost) just data.",
], lead="An explorable picture of a project-, programme- or agile-delivery method.")
d.table("Technology stack", ["Layer", "Technology"], [
    ["Backend", "FastAPI + SQLAlchemy + SQLite (Python 3.12)"],
    ["Front end", "React 19 + Vite, react-force-graph-2d"],
    ["Exports", "openpyxl (CSV/Excel), reportlab (PDF)"],
    ["Packaging", "Docker (multi-stage), single image"],
    ["Hosting", "Render — Docker web service"],
], col_widths=[3.5, 8.6])
d.image("Deployment architecture", A("arch_deployment.png"),
        lead="One container serves the API and the built React app — a single origin.")
d.image("Data model", A("arch_datamodel.png"),
        lead="Framework → entities → relationships; each framework's config (types/codes/lanes/phases) makes the app generic — adding MSP or SAFe is a data file.")
d.image("The graph link model", A("arch_graph_model.png"),
        lead="Contains, direct and derived links are built from activity-centric data.")
d.bullets("Two fixed layouts", [
    ("Matrix — processes top, activities beneath, products below; roles left, practices right, approaches bottom.", NAVY),
    ("Timeline — lifecycle swimlanes (Directing / Managing / Delivering) with a stage scrubber.", NAVY),
    "Both pin node positions; node size reflects direct responsibilities (C/P/N/I/O/U/A count).",
], lead="Positional meaning instead of an organic blob.")
d.bullets("Security & deployment", [
    "Reads are open (public reference, no personal data).",
    "Writes need a single admin password (X-Admin-Password header).",
    "Render Blueprint: one service per framework (FRAMEWORK_KEY + APP_BASE); push to main auto-deploys all.",
    "Shared front door apps.p3mai.com (apps-gateway) routes /prince2, /msp, /safe.",
    "DB auto-seeds its framework on boot — ephemeral disk, so edits reset on redeploy.",
])
d.table("Key design decisions", ["Decision", "Why"], [
    ["Config-driven, framework-agnostic model", "PRINCE2, MSP & SAFe on one codebase; new method = data"],
    ["One image, one service per framework", "FRAMEWORK_KEY selects each; shared front door"],
    ["Activity-centric relationships", "One row per real mark; higher links derived"],
    ["Fixed layouts + direct_degree size", "Readable structure; stable weighting"],
], col_widths=[5.0, 7.1])
d.bullets("Roadmap", [
    ("Done — MSP, SAFe 6.0 Essential and PMBOK 6th ed are live behind the front door.", NAVY),
    "SME-verify the indicative activity breakdowns / PMBOK ITTO cross-references.",
    "Extend SAFe beyond Essential; consider PMBOK 7/8 (principles + performance domains).",
    "Persistent storage (disk / Postgres) so authoring edits survive redeploys.",
])
d.save(os.path.join(DOCS, "01_Architecture_and_Design_Summary.pptx"))
print("wrote 01 deck")


# ============ 02 — User Manual ============
d = Deck("DOC-02", "OFFICIAL")
d.title_slide("User Manual", "Using the P3MAI Method Map — summary")
d.bullets("What the Method Map does", [
    "Turns a method's cross-reference into an explorable network — PRINCE2, MSP or SAFe.",
    "See which roles, practices/competencies, and products/artefacts each activity touches.",
    "Tailor engagements, onboard teams, and explain governance visually.",
], lead="A picture of how a method fits together — this deck uses PRINCE2 as the example.")
d.image("The screen at a glance", A("ui_explorer.png"),
        lead="Sidebar · control panel · graph stage · detail panel.")
d.table("Reading the codes", ["Where", "Codes"], [
    ["Roles / practices / approaches", "C Responsible · P Participates · N Assists"],
    ["Products", "I Input · O Output · U Update · A Authorise"],
], col_widths=[5.2, 6.9], lead="The most important thing to learn — labels on every link.")
d.bullets("The Matrix layout", [
    "Processes top, activities beneath, products in a band below.",
    "Roles left, practices right, management approaches along the bottom.",
    "Bigger nodes = more direct responsibilities.",
    "Drag to pan, scroll to zoom, click a node for detail.",
])
d.bullets("The Timeline layout", [
    "Processes in swimlanes (Directing / Managing / Delivering), left→right in order.",
    "A scrubber walks the lifecycle stage by stage.",
    "Play to auto-advance; Spotlight one stage, or Cumulative to build up.",
    "Reset (gold button) clears the selection and scrubber back to the full view.",
], lead="Watch the project unfold over time.")
d.bullets("Select a node → the detail panel", [
    "The node glows gold; its neighbours stay bright, the rest dim.",
    "The panel lists every relationship, with codes and owning process.",
    "A process lists its activities in sequence.",
    "Export a PDF summary or a CSV of just that element.",
])
d.bullets("Project Lifecycle view", [
    "The classic PRINCE2 process model as a swimlane.",
    "Time runs left→right: Pre-project → Initiation → Delivery ⟳ → Final.",
    "Click a process to see its activities in sequence; jump into the graph.",
])
d.table("Exporting", ["Export", "Gives you"], [
    ["Graph as PNG", "A picture of the current view for slides"],
    ["CSV / Excel", "The whole cross-reference as a spreadsheet"],
    ["Entity PDF", "A branded one-element relationship summary"],
], col_widths=[3.6, 8.5])
d.bullets("The other frameworks (same tool)", [
    "MSP 5th ed — programme processes across Identify → Define → Delivery ⟳ → Close; codes C/P/N, CO/CR/RF/RV/UP/IM.",
    "SAFe 6.0 Essential — events across the PI cadence (PI Planning → Iterations ⟳ → IP → Inspect & Adapt); codes F/A/P/I and I/C/U/R/E.",
    "PMBOK 6th ed — the 49-process matrix, 10 Knowledge Areas × 5 Process Groups; codes I/O (inputs/outputs) and T (tools).",
    "Same screens and exports; only the layers and codes differ. The Guide always describes the map you're on.",
], lead="Open each at apps.p3mai.com/prince2 · /msp · /safe · /pmbok.")
d.bullets("Good to know", [
    "First load after a quiet spell can take up to a minute (the app wakes).",
    "A dashed ring means the data is indicative — verify before formal use.",
    "Authoring mode (password) lets authorised users correct the data.",
])
d.save(os.path.join(DOCS, "02_User_Manual_Summary.pptx"))
print("wrote 02 deck")


# ============ 03 — Operation Manual ============
d = Deck("DOC-03", "OFFICIAL-SENSITIVE")
d.title_slide("Operation Manual", "Running, deploying & maintaining the Method Map — summary")
d.table("System at a glance", ["Item", "Value"], [
    ["Repository", "github.com/DRC63/method-map (+ apps-gateway front door)"],
    ["Production", "Render Docker web services — Starter, Oregon — one per framework"],
    ["Services", "method-map · msp- · safe- · pmbok-method-map"],
    ["Live URLs", "apps.p3mai.com/prince2 · /msp · /safe · /pmbok"],
    ["Database", "SQLite, auto-seeds its FRAMEWORK_KEY on boot; ephemeral"],
    ["Dev ports", "backend 8002 · frontend 5175"],
], col_widths=[3.2, 8.9])
d.table("Configuration (env vars)", ["Variable", "Purpose"], [
    ["FRAMEWORK_KEY", "Which framework this service seeds + serves (prince2-7 / msp-5 / safe-essential)"],
    ["APP_BASE", "SPA base path for the front door (/prince2/ · /msp/ · /safe/)"],
    ["ADMIN_PASSWORD", "Fail-closed: no default; unset = read-only; distinct secret per service"],
    ["DATABASE_URL", "SQLAlchemy URL; point at Postgres to persist"],
    ["PORT", "Set by Render automatically"],
], col_widths=[3.8, 8.3])
d.bullets("Running locally", [
    "Backend: venv → pip install → python -m app.seed → uvicorn …:app --port 8002.",
    "Front end: npm install → npm run dev -- --port 5175.",
    "Registered in .claude/launch.json as method-map-backend / -frontend.",
])
d.bullets("Data management", [
    "Auto-seeds from seed_data/*.json when the DB is empty.",
    "Reseed: python -m app.seed --force.",
    "Corrections not in the spreadsheet go in the CORRECTIONS list in the extractor.",
    "After a schema change, delete the DB then reseed (create_all won't alter columns).",
])
d.bullets("Deployment", [
    ("Push to main → Render auto-builds and deploys every framework service.", NAVY),
    "One image per framework; FRAMEWORK_KEY + APP_BASE differ, nothing else.",
    "DB re-seeds on boot, so bundled-data changes go live automatically.",
    "New framework: add render.yaml service → sync Blueprint + set ADMIN_PASSWORD → add apps-gateway route.",
    "In-app authoring edits are lost on redeploy (ephemeral disk).",
])
d.table("Front door (apps.p3mai.com)", ["Slug", "Service"], [
    ["/prince2", "method-map.onrender.com"],
    ["/msp", "msp-method-map.onrender.com"],
    ["/safe", "safe-method-map.onrender.com"],
    ["/pmbok", "pmbok-method-map.onrender.com"],
], col_widths=[2.6, 6.7],
    lead="apps-gateway reverse proxy strips the slug; one line per framework in ORIGINS.")
d.bullets("Monitoring & health", [
    "Health probe: GET /api/health → {status: ok} (Render's deploy check).",
    "Render dashboard → Logs (live tail) and Metrics.",
    "A plain 404 right after deploy is routing propagation — retry shortly.",
])
d.table("Troubleshooting (top items)", ["Symptom", "Fix"], [
    ["Data reverted after deploy", "Expected — put durable changes in the seed, or add persistence"],
    ["Writes rejected (401)", "Re-enter admin password; check ADMIN_PASSWORD in Render"],
    ["New column missing", "Delete DB and reseed"],
    ["Slow first hit", "Instance woke from sleep — wait"],
], col_widths=[4.6, 7.5])
d.bullets("Backup & persistence", [
    "The authoritative data is the seed JSON in Git — that is the backup.",
    "The running DB is disposable, rebuilt on every boot.",
    "For durable edits: attach a Render disk or migrate to Postgres.",
])
d.save(os.path.join(DOCS, "03_Operation_Manual_Summary.pptx"))
print("wrote 03 deck")
print("done")
