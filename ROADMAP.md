# P3MAI Method Map — Roadmap

_Last updated: 2 August 2026._

A living view of where the Method Map is and where it could go. Grouped **Now /
Next / Later**; the **Done** section keeps recent milestones for context. Nothing
below is a commitment — it's a shared backlog to prioritise against.

---

## ✅ Done (recent milestones)

- **Four frameworks live** behind the shared front door `apps.p3mai.com` — each its
  own Render service from one codebase (`FRAMEWORK_KEY` + `APP_BASE`):
  - PRINCE2 7 → `/prince2` · MSP 5th ed → `/msp` · SAFe 6.0 Essential → `/safe` ·
    PMBOK 6th ed → `/pmbok`.
- **Config-driven, framework-agnostic engine** — a new method is (almost) just a
  seed JSON: `types` (container/hub/node + zone), `codes`, `lanes`, `phases`.
- **PMBOK hub-grid** (`lifecycle_layer: "hub"`) renders the 5 Process Groups × 10
  Knowledge Areas matrix in the Lifecycle and Timeline views; `label_below` centres
  the Matrix spine.
- **Timeline Reset** control; 4-way Guide cross-links (data-driven, one-line add).
- **Docs** DOC-01/02 at v1.3, DOC-03 at v1.2; website Services buttons for all four.

---

## 🟢 Now (immediate, in flight)

- **SME-verify the indicative data.** Framework *names* and PMBOK's PG×KA grid are
  *confirmed*; the MSP/SAFe activity breakdowns, all cross-reference marks, and
  PMBOK's ITTO links are *indicative* best-effort reconstructions. Verify against
  the licensed manuals / bodies of knowledge before any formal, training, audit or
  commercial use. Corrections should flow through the builder scripts
  (`build_msp.py` / `build_safe.py` / `build_pmbok.py`) so they persist in git.

---

## 🔵 Next (near-term, worthwhile)

- **Persistent storage** (Render disk or Postgres). Today the DB is ephemeral and
  auto-seeds on boot, so in-app authoring edits are lost on redeploy. Needed if SMEs
  will correct data *in the app*; otherwise corrections must go via the builder
  scripts. Unblocks a smoother verification workflow (see _Now_).
- **PMBOK Matrix band-height polish.** With 66 Inputs/Outputs + 62 Tools stacked as
  two bands, they wrap at 7 per row and run tall. Make the per-row node count
  config-driven so wide layers render wider/shorter.
- **Documentation upkeep** — keep DOC-01/02/03 in step as features land (they are
  generated from `docs/_source/gen_*.py`; edit + re-run).

---

## 🟣 Later (opportunities)

- **SAFe beyond Essential** — add the Portfolio and Large Solution levels (a larger
  seed, more lanes/roles/artefacts).
- **PMBOK 7th / 8th edition companion** — the 8th ed (2025) is current and the PMP
  exam moved to it in July 2026. Principles + performance domains (+ the
  reintroduced focus-area processes) could be a separate framework or an overlay on
  PMBOK 6.
- **More frameworks** — the engine is proven across four structurally different
  methods; candidates include ISO 21500/21502, PRINCE2 Agile, or a Scrum/Kanban map.
- **Single-service + in-app framework switcher (Option C)** — sketched (~2 days, $0
  extra hosting; rendering is already config-driven, only the `list[0]` selection is
  hardcoded). **Declined for now** — the separate-app-per-method feel is preferred.
  Revisit if the suite grows or per-service hosting cost becomes a factor.
- **Saved per-engagement tailored views** — the schema already anticipates this
  (a curated subset of layers/entities saved and shareable per client).
- **Optional user accounts** — only if the tool ever holds sensitive or per-client
  data; today reads are open and writes use a single shared admin password.

---

## Notes

- **IP / trademarks.** PRINCE2® and MSP® (AXELOS/PeopleCert), SAFe® (Scaled Agile,
  Inc.), and PMBOK®/PMI®/PMP® (Project Management Institute, Inc.) are the marks of
  their owners. The Method Map is an independent reference tool, not affiliated with
  or endorsed by any of them; it reconstructs factual structure and names with
  original descriptions and carries the appropriate disclaimers.
- **Hosting.** Each framework is a Starter Render service; Free tier (with a ~50s
  cold start) is a per-service option if cost matters. The website is on Rise and is
  **not** git-auto-deployed — publishing a site change means uploading the changed
  files to Rise.
