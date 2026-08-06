"""Generate 03_Operation_Manual.docx for the P3MAI Method Map."""
import os
import docstyle as ds

OUT = os.path.join(os.path.dirname(__file__), "..", "03_Operation_Manual.docx")
VERSION = "v1.3"
DATE = "6 August 2026"

doc = ds.new_doc()
ds.footer(doc, "OFFICIAL-SENSITIVE", VERSION)
ds.title_page(doc, "DOC-03", "Operation Manual",
              "Running, deploying and maintaining the Method Map",
              VERSION, DATE, "Douglas Colvin, P3MAI", "OFFICIAL-SENSITIVE")
ds.doc_control(doc, [
    ["v1.0", "2026-08-01", "Douglas Colvin", "Initial issue"],
    ["v1.1", "2026-08-02", "Douglas Colvin",
     "Multi-framework update: MSP and SAFe services; one-service-per-framework "
     "Blueprint; FRAMEWORK_KEY seeding; front-door (apps-gateway) routing; runbook "
     "for adding a framework deployment."],
    ["v1.2", "2026-08-02", "Douglas Colvin",
     "Fourth framework: PMBOK 6th ed (pmbok-method-map service, /pmbok route, "
     "build_pmbok.py)."],
    ["v1.3", "2026-08-06", "Douglas Colvin",
     "Fail-closed admin auth (SEC-05): no default password, unset = read-only; per-service "
     "passwords still to be set (SEC-07). CI + Dependabot (ENG-01/SEC-03); optional Sentry "
     "(ENG-05, activates on SENTRY_DSN)."],
])
ds.add_toc(doc)

# 1
ds.heading(doc, "1.  Purpose & audience", 1)
ds.para(doc, "This manual is for whoever runs and maintains the **P3MAI Method Map** — locally, and on "
        "Render. It covers configuration, data management, deployment, monitoring, backup, security "
        "operations, troubleshooting and a set of routine runbooks. Architecture is in **DOC-01**; "
        "end-user guidance is in **DOC-02**.")

# 2 system summary
ds.heading(doc, "2.  System summary", 1)
ds.table(doc, ["Item", "Value"], [
    ["What", "Single-origin web app: FastAPI backend serving a React SPA, SQLite database"],
    ["Repository", "github.com/DRC63/method-map (private, DRC63); front door: github.com/DRC63/apps-gateway"],
    ["Production", "Render Docker web services, Starter plan, Oregon — one per framework"],
    ["Frameworks / services", "prince2-7 → method-map · msp-5 → msp-method-map · safe-essential → safe-method-map · pmbok-6 → pmbok-method-map"],
    ["Live URLs", "apps.p3mai.com/prince2 · /msp · /safe · /pmbok (each also <service>.onrender.com)"],
    ["Front door", "apps.p3mai.com — Node reverse proxy strips the slug and forwards to each service"],
    ["Database", "SQLite (methodmap.db), auto-seeded on boot; ephemeral on Render"],
    ["Dev ports", "backend 8002, frontend 5175 (one framework at a time, via FRAMEWORK_KEY)"],
], col_widths=[3.6, 11.9])

# 3 configuration
ds.heading(doc, "3.  Configuration", 1)
ds.para(doc, "All configuration is via environment variables (a local `.env` file in `backend/` is read "
        "automatically; in production set them in the Render dashboard).")
ds.table(doc, ["Variable", "Default", "Purpose"], [
    ["FRAMEWORK_KEY", "(unset)", "Which framework this deployment seeds + serves (prince2-7 / msp-5 / safe-essential / pmbok-6). Unset = seed all (local dev)."],
    ["APP_BASE", "/", "Build-time base path the SPA is built under (/prince2/, /msp/, /safe/) so it works behind the front door."],
    ["ADMIN_PASSWORD", "(no default — fail-closed)", "Unlocks authoring mode. Unset = service is read-only; set a distinct generated secret per service (SEC-07)."],
    ["DATABASE_URL", "sqlite:///…/methodmap.db", "SQLAlchemy URL; point at Postgres to persist."],
    ["CORS_ORIGINS", "http://localhost:5173", "Allowed origins (only relevant in split local dev)."],
    ["PORT", "8000", "Set by Render automatically; the container binds to it."],
], col_widths=[3.6, 4.0, 7.9])
ds.callout(doc, "note", "FRAMEWORK_KEY is per-service",
           ["Each Render service pins one FRAMEWORK_KEY, so its ephemeral DB auto-seeds exactly one "
            "framework. Locally, leaving it unset seeds all three; setting it (e.g. for a review) "
            "seeds just that one — delete methodmap.db first so the empty-DB boot re-seed runs."])
ds.callout(doc, "note", "Change the admin password",
           ["The default `change-me` must never reach production. It is set as a Render dashboard secret "
            "(sync:false in render.yaml), so it lives only in Render, not the repo."])

# 4 running locally
ds.heading(doc, "4.  Running locally", 1)
ds.para(doc, "The two dev servers are registered in the working-directory `.claude/launch.json` as "
        "`method-map-backend` (port 8002) and `method-map-frontend` (port 5175).")
ds.heading(doc, "4.1  Backend", 2)
ds.code_block(doc,
              "cd backend\n"
              "python -m venv venv\n"
              ".\\venv\\Scripts\\Activate.ps1\n"
              "pip install -r requirements.txt\n"
              "python -m app.seed        # first time only\n"
              "uvicorn app.main:app --reload --port 8002")
ds.para(doc, "API docs are then at http://localhost:8002/docs.")
ds.heading(doc, "4.2  Front end", 2)
ds.code_block(doc,
              "cd frontend\n"
              "npm install\n"
              "npm run dev -- --port 5175")
ds.para(doc, "The app runs at http://localhost:5175 and proxies `/api/*` to the backend on 8002.")

# 5 data management
ds.heading(doc, "5.  Data management", 1)
ds.heading(doc, "5.1  How seeding works", 2)
ds.para(doc, "On boot, if the database has no frameworks, the app loads the bundled `*.json` files in "
        "`backend/app/seed_data/` — `prince2-7.json`, `msp-5.json`, `safe-essential.json` and "
        "`pmbok-6.json`. If "
        "`FRAMEWORK_KEY` is set (as on each production service) only that one is seeded; unset (local "
        "dev) seeds all three. This is idempotent and is how a fresh or restarted container comes up "
        "populated.")
ds.heading(doc, "5.2  Reseeding", 2)
ds.para(doc, "To wipe and reload the bundled data:")
ds.code_block(doc, "cd backend\npython -m app.seed --force")
ds.heading(doc, "5.3  Making a data correction", 2)
ds.para(doc, "The dataset is generated from the source spreadsheet by "
        "`backend/scripts/extract_prince2.py`. **Corrections that are not in the spreadsheet** go in the "
        "`CORRECTIONS` list inside that script, so they survive regeneration. After editing it:")
ds.code_block(doc,
              "cd backend\n"
              "python scripts/extract_prince2.py    # regenerates seed_data/prince2-7.json\n"
              "python -m app.seed --force           # reload into the DB")
ds.callout(doc, "tip", "Example correction already in place",
           ["The 'Escalate issues and risks' activity was made to output an Issue Report via a "
            "CORRECTIONS entry — a worked example of the pattern to follow."])
ds.heading(doc, "5.4  Schema changes", 2)
ds.callout(doc, "pitfall", "Delete the DB after a schema change",
           ["SQLAlchemy's create_all makes missing tables but will not add new columns to an existing "
            "table. After changing a model, delete the local database first, then reseed:",
            "`del backend\\methodmap.db*`  then  `python -m app.seed --force`"])
ds.heading(doc, "5.5  Adding a new framework", 2)
ds.para(doc, "MSP and SAFe were both added this way — as data only. Produce a `*.json` in `seed_data/` "
        "in the same shape as the others (a `framework.config` block defining types/codes/lanes/"
        "phases; entities referenced by a `type::name` key; relationships between them). The MSP and "
        "SAFe seeds are generated by **inline builder scripts** (no source spreadsheet):")
ds.code_block(doc,
              "cd backend\n"
              "python -m scripts.build_msp     # regenerates seed_data/msp-5.json\n"
              "python -m scripts.build_safe    # regenerates seed_data/safe-essential.json\n"
              "python -m scripts.build_pmbok   # regenerates seed_data/pmbok-6.json\n"
              "python -m app.seed --force      # reload into the DB")
ds.para(doc, "Drop the file in and reseed — **no code change is required**. Going live also needs a "
        "new Render service (§7.4).")

# 6 authoring admin
ds.heading(doc, "6.  Authoring administration", 1)
ds.para(doc, "Authoring mode lets an authorised editor add/edit/delete entities and relationships in the "
        "running app. Set `ADMIN_PASSWORD`, share it only with editors, and they unlock it under "
        "**Authoring & Admin**. Writes are gated server-side by the `X-Admin-Password` header.")
ds.callout(doc, "pitfall", "In-app edits are not durable on Render",
           ["Render's disk is ephemeral, so authoring edits are lost on the next redeploy/restart. Until "
            "persistent storage is added, keep authoritative changes in the seed/extractor (§5.3), and "
            "treat in-app editing as a preview/demonstration facility."])

# 7 deployment
ds.heading(doc, "7.  Deployment", 1)
ds.heading(doc, "7.1  How it deploys", 2)
ds.para(doc, "Deployment is via a Render **Blueprint** (`render.yaml`) that defines **one web service "
        "per framework** from the same Docker image — each Starter plan, Oregon, health check "
        "`/api/health`, `ADMIN_PASSWORD` as a dashboard secret, `autoDeploy: true` — differing only "
        "in `FRAMEWORK_KEY` and the `APP_BASE` build arg. A separate repo, **apps-gateway**, is the "
        "front door (its own Render service) and auto-deploys the same way.")
ds.heading(doc, "7.2  Deploying a change", 2)
ds.para(doc, "Because auto-deploy is on, **pushing to `main` redeploys every framework service** (they "
        "all build from the same repo). A data or code change therefore rolls out to prince2, msp and "
        "safe together:")
ds.code_block(doc, "git add -A\ngit commit -m \"...\"\ngit push origin main   # Render rebuilds all services")
ds.para(doc, "Watch each build in the Render dashboard (the service → Events / Logs). The database "
        "re-seeds on boot, so bundled-data changes go live automatically; in-app edits are lost.")
ds.heading(doc, "7.3  Rollback", 2)
ds.para(doc, "In the Render dashboard, open the affected service → **Events**, find the previous good "
        "deploy and choose **Redeploy**, or revert the commit on `main` and push.")
ds.heading(doc, "7.4  Adding a framework service", 2)
ds.para(doc, "After the seed JSON exists (§5.5), add a service block to `render.yaml` (copy an existing "
        "one; set `FRAMEWORK_KEY` and `APP_BASE=/<slug>/`) and push. Then, in the Render dashboard, "
        "**sync the Blueprint** to create the new service and set its **`ADMIN_PASSWORD`** secret "
        "(it is `sync:false`, so it is not seeded automatically). Finally add the route to the front "
        "door: one line in `apps-gateway`'s `ORIGINS` (slug → `<service>.onrender.com`) and a "
        "landing-page card, then push that repo.")
ds.callout(doc, "note", "SAFe & PMBOK worked examples (2 Aug 2026)",
           ["SAFe then PMBOK each went live exactly this way — e.g. `pmbok-method-map` "
            "(FRAMEWORK_KEY=pmbok-6, APP_BASE=/pmbok/) + a `/pmbok` route in apps-gateway. The only "
            "manual steps were the Blueprint sync and setting ADMIN_PASSWORD."])

# 8 domain
ds.heading(doc, "8.  Domain & the front door", 1)
ds.para(doc, "All frameworks are reached under one domain — **apps.p3mai.com** — via the `apps-gateway` "
        "reverse proxy, which routes `/prince2`, `/msp` and `/safe` (and the PMO apps) to their "
        "services. Each service is also directly reachable at `<service>.onrender.com`. This front "
        "door replaced the earlier per-app subdomain approach (e.g. prince2.p3mai.com), so no new "
        "custom-domain slots are consumed per framework.")
ds.para(doc, "Adding a framework to the front door is one line in `apps-gateway`'s `ORIGINS` map "
        "(`<slug>` → `<service>.onrender.com`) plus a landing-page card — then push (it auto-deploys).")

# 9 website
ds.heading(doc, "9.  Website integration", 1)
ds.para(doc, "The P3MAI website's Services page links to the maps: a **PRINCE2 Method Map** and a "
        "**SAFe Method Map** button on the Project Management card, and an **MSP Method Map** button "
        "on the Programme Management card. Each is env-aware in the site's `script.js`: a "
        "`localhost:<port>` sentinel in local dev, rewritten to the front-door URL "
        "(`apps.p3mai.com/<slug>`) in production. The site is on Rise hosting (not auto-deployed from "
        "GitHub), so publishing a button means uploading `services.html` + `script.js` to Rise; bump "
        "the `script.js?v=` query to bust Rise's edge cache.")
ds.callout(doc, "pitfall", "Don't hardcode the localhost link",
           ["The `localhost:<port>` href in the website's services.html is intentional — script.js "
            "rewrites it in production. Replacing it with a hardcoded URL breaks local dev."])

# 10 monitoring
ds.heading(doc, "10.  Monitoring & health", 1)
ds.bullet(doc, "**Health probe** — `GET /api/health` returns `{\"status\":\"ok\"}`. Render uses it as the "
          "deploy health check.")
ds.bullet(doc, "**Logs / metrics** — in the Render dashboard, the service → **Logs** (live tail) and "
          "**Metrics**. On boot you should see \"Your service is live\" and repeated 200s on /api/health.")
ds.bullet(doc, "**Cold start** — on the Starter plan the service stays warm; on the free plan it sleeps "
          "after inactivity (~50s wake). A plain-text 404 immediately after deploy is usually routing "
          "propagation — retry after a few seconds.")

# 11 backup
ds.heading(doc, "11.  Backup & persistence", 1)
ds.para(doc, "The authoritative data is the **seed JSON in the Git repository** — that is the backup; the "
        "running database is disposable and rebuilt from it on every boot. To make in-app edits durable, "
        "either attach a Render persistent disk (and point `DATABASE_URL` at a file on it) or migrate to "
        "Postgres (set `DATABASE_URL` to the Postgres URL).")

# 12 security ops
ds.heading(doc, "12.  Security operations", 1)
ds.bullet(doc, "**Read access is open** by design — no accounts, no personal data.")
ds.bullet(doc, "**Rotate the admin password** by changing `ADMIN_PASSWORD` in the Render dashboard and "
          "re-saving (triggers a redeploy). Editors' browsers will need the new password re-entered.")
ds.bullet(doc, "**Classification** — this manual is OFFICIAL-SENSITIVE because it references the admin "
          "secret's existence and deployment specifics; handle accordingly.")

# 13 troubleshooting
ds.heading(doc, "13.  Troubleshooting", 1)
ds.table(doc, ["Symptom", "Likely cause", "Fix"], [
    ["Plain 'Not Found' right after deploy", "Edge routing not yet propagated", "Wait a few seconds and retry; check Logs show 'service is live'"],
    ["App slow on first hit", "Instance woke from sleep (free plan)", "Wait for wake; consider Starter plan (already in use)"],
    ["Data reverted after deploy", "Ephemeral disk re-seeded", "Expected; put durable changes in the seed (§5.3) or add persistence"],
    ["Graph doesn't render", "Old cache / JS error", "Hard-refresh; check the browser console; confirm /api/frameworks returns JSON"],
    ["Authoring writes rejected (401)", "Wrong/missing admin password", "Re-enter under Authoring & Admin; confirm ADMIN_PASSWORD in Render"],
    ["New column missing after model change", "create_all won't alter tables", "Delete the DB and reseed (§5.4)"],
    ["Build fails on Render", "Dependency or Dockerfile issue", "Read the build log; reproduce locally with docker build"],
], col_widths=[4.2, 4.3, 7.0])

# 14 runbooks
ds.heading(doc, "14.  Routine runbooks", 1)
ds.heading(doc, "14.1  Reseed production data", 2)
ds.para(doc, "Edit the seed (or extractor), commit and push — Render rebuilds and the DB re-seeds on "
        "boot. No manual DB step is needed in production.")
ds.heading(doc, "14.2  Apply a data correction", 2)
ds.para(doc, "Add an entry to `CORRECTIONS` in `extract_prince2.py`, regenerate the JSON, verify locally "
        "(`python -m app.seed --force`), commit and push.")
ds.heading(doc, "14.3  Rotate the admin password", 2)
ds.para(doc, "Render dashboard → service → **Environment** → edit `ADMIN_PASSWORD` → save (redeploys).")
ds.heading(doc, "14.4  Bring a new framework online", 2)
ds.para(doc, "Build the seed (§5.5) and commit it; add the `render.yaml` service and push; **sync the "
        "Blueprint** in Render and set the new service's `ADMIN_PASSWORD`; add the `apps-gateway` "
        "route and push; confirm `apps.p3mai.com/<slug>/api/health` is OK; add the website button "
        "(§9) and publish to Rise.")

# appendix
ds.heading(doc, "Appendix A — API endpoints", 1)
ds.table(doc, ["Path", "Auth"], [
    ["GET /api/health, /api/meta, /api/frameworks…", "open (read)"],
    ["GET /api/frameworks/{key}/graph | /lifecycle | /export.*", "open (read)"],
    ["GET /api/entities/{id}", "open (read)"],
    ["POST/PUT/DELETE /api/entities | /api/relationships", "admin (X-Admin-Password)"],
], col_widths=[10.5, 5.0])

doc.save(OUT)
print("wrote", os.path.abspath(OUT), os.path.getsize(OUT), "bytes")
