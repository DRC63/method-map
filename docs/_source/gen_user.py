"""Generate 02_User_Manual.docx for the P3MAI Method Map."""
import os
import docstyle as ds

OUT = os.path.join(os.path.dirname(__file__), "..", "02_User_Manual.docx")
ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
VERSION = "v1.1"
DATE = "2 August 2026"

doc = ds.new_doc()
ds.footer(doc, "OFFICIAL", VERSION)
ds.title_page(doc, "DOC-02", "User Manual",
              "Using the P3MAI Method Map",
              VERSION, DATE, "Douglas Colvin, P3MAI", "OFFICIAL")
ds.doc_control(doc, [
    ["v1.0", "2026-08-01", "Douglas Colvin", "Initial issue"],
    ["v1.1", "2026-08-02", "Douglas Colvin",
     "Multi-framework update: the map now hosts PRINCE2, MSP and SAFe. Added the "
     "framework picker / addresses and a section on the SAFe map; PRINCE2 remains the "
     "worked example throughout."],
])
ds.add_toc(doc)

# 1
ds.heading(doc, "1.  Welcome", 1)
ds.para(doc, "The **P3MAI Method Map** turns a management method into an interactive picture. Instead of "
        "reading a cross-reference spreadsheet, you explore the method as a network: see which "
        "**roles** perform each **activity**, which **practices** it draws on, and which **products** "
        "or **artefacts** it takes in or creates.")
ds.para(doc, "It is useful when tailoring an engagement, onboarding a team, or explaining governance "
        "to a client — anywhere you need to see how one part of a method connects to the rest.")
ds.callout(doc, "note", "Three methods, one tool",
           ["The Method Map now covers **three frameworks**, each as its own map with its own layers, "
            "codes and lifecycle: **PRINCE2 7** (projects), **MSP 5th edition** (programmes) and "
            "**SAFe 6.0 Essential** (scaled agile). This manual uses **PRINCE2 as the worked example** "
            "— every screen, control and export works the same way in all three; only the element "
            "types and codes differ (see §12). The in-app **Guide** page always describes the "
            "framework you are looking at."])
ds.heading(doc, "1.1  Who it is for", 2)
ds.para(doc, "Anyone working with these methods — project, programme and portfolio managers, PMO "
        "staff, agile leaders, consultants and those learning a framework. No technical knowledge is "
        "needed.")
ds.heading(doc, "1.2  Getting in", 2)
ds.para(doc, "Open the Method Map in a web browser — each framework has its own address behind the "
        "shared front door:")
ds.table(doc, ["Framework", "Address"], [
    ["PRINCE2 7", "apps.p3mai.com/prince2"],
    ["MSP 5th edition", "apps.p3mai.com/msp"],
    ["SAFe 6.0 Essential", "apps.p3mai.com/safe"],
], col_widths=[5.0, 10.5])
ds.para(doc, "Or reach them from the **Project Management** and **Programme Management** cards on the "
        "P3MAI website's Services page. Nothing to install, no login to read.")
ds.callout(doc, "tip", "First visit may be slow",
           ["The app sleeps when idle to save hosting cost. The first page load after a quiet spell can "
            "take up to a minute while it wakes — after that it is instant."])

# 2 interface
ds.heading(doc, "2.  The screen at a glance", 1)
ds.figure(doc, os.path.join(ASSETS, "ui_explorer.png"),
          "Figure 1 — The Method Explorer screen.")
ds.table(doc, ["Area", "What it holds"], [
    ["Sidebar (far left)", "Switch between Method Explorer, Project Lifecycle, Guide and Authoring & Admin."],
    ["Control panel (left)", "Search, layout switch, layer toggles, the legend, and export buttons."],
    ["Graph stage (centre)", "The network itself — pan, zoom and click here."],
    ["Detail panel (right)", "Appears when you select a node; lists its relationships and its exports."],
], col_widths=[4.0, 11.5])

# 3 codes
ds.heading(doc, "3.  Reading the codes and colours", 1)
ds.para(doc, "Every connection in the map is labelled with a cross-reference code. These are the most "
        "important thing to learn. The codes below are **PRINCE2's**; MSP and SAFe use their own "
        "(see §12), and the in-app control-panel legend and Guide always show the set for the "
        "framework you are viewing.")
ds.table(doc, ["Where", "Codes"], [
    ["Roles, practices, approaches", "C = Responsible · P = Participates · N = Assists"],
    ["Management products", "I = Input · O = Output · U = Update · A = Authorise"],
], col_widths=[5.0, 10.5])
ds.para(doc, "Each type of element has its own colour, used consistently everywhere:")
ds.table(doc, ["Colour", "Element type"], [
    ["Navy", "Processes"],
    ["Steel blue", "Activities"],
    ["Gold", "Management team roles"],
    ["Green", "Practices"],
    ["Purple", "Management approaches"],
    ["Red", "Management products"],
], col_widths=[4.0, 11.5])
ds.callout(doc, "note", "The dashed ring",
           ["A node drawn with a dashed ring is marked *indicative* — a best-effort reconstruction of "
            "the activity-level detail. Treat it as a well-reasoned first pass and verify against the "
            "PRINCE2 manual before using it as formal evidence."])

# 4 explorer
ds.heading(doc, "4.  The Method Explorer", 1)
ds.para(doc, "The Explorer is the network graph. Two layouts are available — pick one with the "
        "**Matrix / Timeline** switch at the top of the control panel.")
ds.heading(doc, "4.1  The Matrix layout", 2)
ds.para(doc, "A fixed hierarchy that stays put so you always know where to look:")
ds.bullet(doc, "**Processes** run across the top; **Activities** are stacked beneath their process;")
ds.bullet(doc, "**Products** sit in a band below the activities;")
ds.bullet(doc, "**Roles** are pinned to the left, **Practices** to the right, and **Management "
          "approaches** along the bottom.")
ds.para(doc, "Bigger nodes have more **direct responsibilities** — the more C/P/N/I/O/U/A relationships "
        "an element takes part in, the larger it is drawn. The Project Manager and the busy products "
        "(Business Case, Plan, the registers) stand out.")
ds.heading(doc, "4.2  Moving around", 2)
ds.table(doc, ["To…", "Do this"], [
    ["Pan", "Drag an empty part of the graph"],
    ["Zoom", "Scroll (mouse wheel) or pinch"],
    ["Move a node", "Drag the node itself"],
    ["See details", "Click a node"],
    ["Clear a selection", "Click an empty part of the graph"],
], col_widths=[3.5, 12.0])
ds.heading(doc, "4.3  Selecting a node", 2)
ds.para(doc, "Click any node and it is highlighted with a gold glow and enlarged, its neighbours stay "
        "bright while everything else dims, and the **detail panel** opens on the right (see §6). "
        "Hovering (without clicking) does the same highlighting temporarily.")
ds.heading(doc, "4.4  Layers", 2)
ds.para(doc, "Under **Layers** you can switch any element type on or off — hide Products to study just "
        "roles and practices, for example. The count next to each layer shows how many of that type exist.")
ds.heading(doc, "4.5  Indirect links", 2)
ds.para(doc, "With **Activities** hidden, turn on **Show indirect (co-occurrence) links** to connect any "
        "two elements that share an activity — so you can study, say, which Roles work with which "
        "Products, without the activity detail in the way.")
ds.heading(doc, "4.6  Search", 2)
ds.para(doc, "Type in the **Search** box to highlight every element whose name matches — handy for "
        "finding a specific product or role in a busy graph.")

# 5 timeline
ds.heading(doc, "5.  The Timeline layout", 1)
ds.para(doc, "The Timeline layout arranges the method like the project lifecycle: processes in three "
        "swimlanes — **Directing**, **Managing**, **Delivering** — laid out left→right in the order they "
        "run, with activities beneath each process and the roles/practices/approaches/products in bands "
        "below.")
ds.para(doc, "A **scrubber** appears along the bottom. Use it to walk the project stage by stage:")
ds.table(doc, ["Control", "Effect"], [
    ["▶ Play / ❚❚ Pause", "Auto-advance through the seven processes, ~1.6s each"],
    ["Slider / stage ticks", "Jump to any stage (SU, DP, IP, CS, MP, SB, CP)"],
    ["Spotlight", "Highlight only the current stage's process, activities and what they touch"],
    ["Cumulative", "Highlight everything from the start up to the current stage — watch the footprint grow"],
], col_widths=[4.2, 11.3])
ds.callout(doc, "tip", "Tell the story of a project",
           ["Switch to Cumulative and press Play. Watch products and involvement accumulate as the "
            "project moves from Starting Up through to Closing — a quick way to show a client how the "
            "method unfolds over time."])

# 6 detail
ds.heading(doc, "6.  The detail panel", 1)
ds.para(doc, "When you select a node, the detail panel lists everything it connects to, grouped and "
        "labelled with the codes:")
ds.bullet(doc, "an **activity** shows what it uses and produces;")
ds.bullet(doc, "a **role, practice, approach or product** shows the activities that reference it, and "
          "the process each belongs to;")
ds.bullet(doc, "a **process** lists its activities in sequence.")
ds.para(doc, "Click any listed item to jump to it. Two export buttons let you save a **PDF summary** of "
        "the selected element or a **CSV** of just its relationships.")

# 7 lifecycle
ds.heading(doc, "7.  The Project Lifecycle view", 1)
ds.para(doc, "The **Project Lifecycle** view (in the sidebar) is the classic PRINCE2 process model: time "
        "runs left→right (Pre-project → Initiation → Delivery stages ⟳ → Final stage) across the three "
        "swimlanes. **Directing a Project** spans the top; the delivery processes repeat.")
ds.para(doc, "Click any process to see its activities listed in the order they run. Each activity, and "
        "the process itself, links straight into the graph so you can explore its connections.")

# 8 guide
ds.heading(doc, "8.  The Guide", 1)
ds.para(doc, "The **Guide** page is a short, plain-English explainer of the six layers, the codes and "
        "the confidence flags — a good first stop for anyone new to the map or to PRINCE2.")

# 9 exports
ds.heading(doc, "9.  Exporting", 1)
ds.table(doc, ["Export", "How", "Gives you"], [
    ["Graph image", "Export → Graph as PNG (control panel)", "A picture of the current view for slides/reports"],
    ["Full data", "Export → CSV or Excel", "The whole cross-reference as a spreadsheet"],
    ["Entity PDF", "Detail panel → PDF summary", "A branded one-element relationship summary"],
    ["Entity CSV", "Detail panel → CSV (this entity)", "Just the selected element's relationships"],
], col_widths=[3.2, 5.3, 7.0])

# 10 authoring
ds.heading(doc, "10.  Authoring mode (authorised users)", 1)
ds.para(doc, "If you have the admin password you can correct or extend the data. Open **Authoring & "
        "Admin**, enter the password, and editing controls appear in the Explorer: an **+ Add entity** "
        "button, and **Edit / + Relationship / Delete** in each node's detail panel. Set an item's "
        "confidence to *confirmed* once you have verified it against the manual — the dashed ring "
        "disappears. Full procedures are in the **Operation Manual (DOC-03)**.")
ds.callout(doc, "pitfall", "Edits are not permanent yet",
           ["On the current hosting, authoring edits are held in a database that resets when the app is "
            "redeployed. Treat in-app edits as provisional until persistent storage is added, and keep "
            "the authoritative corrections in the data file (see the Operation Manual)."])

# 11 FAQ
ds.heading(doc, "11.  Tips & FAQ", 1)
ds.table(doc, ["Question", "Answer"], [
    ["The graph looks empty / faint", "You may have hidden a layer, or dimmed everything by selecting a node — click empty space to reset, and check the Layers toggles."],
    ["It won't load first time", "The app was asleep; wait up to a minute for it to wake."],
    ["What does the dashed ring mean?", "The data is indicative (activity-level reconstruction) — verify before formal use."],
    ["Why is one node much bigger?", "Node size reflects how many direct relationships it has — big nodes are the busy elements."],
    ["Can I get this as a spreadsheet?", "Yes — Export → Excel, or CSV, from the control panel."],
], col_widths=[5.0, 10.5])

# 12 other frameworks
ds.heading(doc, "12.  The other frameworks — MSP & SAFe", 1)
ds.para(doc, "The Explorer, Lifecycle, Guide, detail panel and exports all work identically for the "
        "other two frameworks — only the **layers** (element types) and **codes** change. Open each at "
        "its own address (§1.2).")
ds.heading(doc, "12.1  MSP 5th edition (programmes)", 2)
ds.para(doc, "Layers: **Programme processes** and their **activities**, cross-referenced to **roles**, "
        "the seven **themes**, **products** and the seven **principles**. The Lifecycle runs "
        "Identify → Define → Delivery tranches ⟳ → Close across the Sponsoring / Managing / Delivering "
        "swimlanes. Codes: roles & themes **C** Responsible · **P** Related · **N** Assists; products "
        "**CO/CR/RF/RV/UP/IM**; principles **E** Embodies.")
ds.heading(doc, "12.2  SAFe 6.0 Essential (scaled agile)", 2)
ds.para(doc, "SAFe is arranged around the **PI (Program Increment) cadence**, not a project that ends. "
        "Layers: **events** (PI Planning, Iteration Execution, System Demo, ART Sync, IP Iteration, "
        "Inspect & Adapt, the Continuous Delivery Pipeline) and their **activities**, cross-referenced "
        "to **roles** (RTE, Product Management, Scrum Master / Team Coach, Product Owner, Agile Team, "
        "Business Owners, System Architect, Customer), **artefacts** (Vision, Roadmap, backlogs, "
        "Features, Stories, PI Objectives…), the **4 core competencies** and the **10 Lean-Agile "
        "Principles**. The Lifecycle runs Prepare & PI Planning → Execute Iterations ⟳ → IP Iteration "
        "→ Inspect & Adapt across the ART and Team swimlanes.")
ds.table(doc, ["Where", "SAFe codes"], [
    ["Roles → event", "F = Facilitates · A = Accountable · P = Participates · I = Informed"],
    ["Artefacts → event", "I = Input · C = Created · U = Updated · R = Reviewed · E = Elaborated"],
    ["Competencies / Principles", "E = Exercised / Embodies"],
], col_widths=[5.0, 10.5])
ds.callout(doc, "note", "SAFe data is indicative",
           ["As with PRINCE2 and MSP, the SAFe event names, roles, artefacts, competencies and "
            "principles are confirmed vocabulary, but the activity breakdown and cross-reference marks "
            "are an indicative reconstruction — verify against the licensed SAFe body of knowledge "
            "before formal use. SAFe® is a trademark of Scaled Agile, Inc.; this is an independent "
            "tool, not affiliated with Scaled Agile, Inc."])

# 13 glossary
ds.heading(doc, "13.  Glossary", 1)
ds.table(doc, ["Term", "Meaning"], [
    ["Process", "One of the seven PRINCE2 processes (SU, IP, DP, CS, MP, SB, CP)."],
    ["Activity", "A step within a process (there are 41)."],
    ["Management team role", "Executive, Senior User, Project Manager, etc."],
    ["Practice", "Business Case, Plans, Risk, Quality, Progress, Organizing, Issues."],
    ["Management approach", "A defined approach — Risk, Change, Quality, Communication, etc."],
    ["Management product", "A document/baseline the method produces (PID, Business Case, registers, reports)."],
    ["C / P / N", "Responsible / Participates / Assists (roles, practices, approaches)."],
    ["I / O / U / A", "Input / Output / Update / Authorise (products)."],
], col_widths=[4.2, 11.3])

doc.save(OUT)
print("wrote", os.path.abspath(OUT), os.path.getsize(OUT), "bytes")
