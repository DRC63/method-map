"""Build seed_data/safe-essential.json for the SAFe (Scaled Agile Framework)
Essential-configuration Method Map.

Like build_msp.py (and unlike extract_prince2.py, which reads a spreadsheet),
this file holds the data inline. The framework vocabulary — the events, roles,
artifacts, the 4 Essential core competencies and the 10 Lean-Agile Principles —
is confirmed SAFe terminology, but the ACTIVITY breakdown of each event and
every cross-reference mark are an **indicative, best-effort reconstruction** of
the SAFe 6.0 Essential model, to be SME-verified against the licensed SAFe body
of knowledge before formal use. No SAFe copyrighted text is reproduced; only
event/role/artifact names and cross-reference marks.

Scope = **Essential SAFe** (Team + ART levels). Portfolio / Large Solution are a
later phase (a bigger seed, more lanes).

The horizontal axis is the **PI cadence** (a repeating Program Increment), not a
project start->finish lifecycle — SAFe is continuous. The Continuous Delivery
Pipeline is modelled as a `throughout` spanning bar.

Codes:
  Roles -> event (who does what):
    F = Facilitates   A = Accountable   P = Participates   I = Informed
  Artifacts -> event (how an artifact is handled):
    I = Input   C = Created   U = Updated   R = Reviewed   E = Elaborated
  Competencies -> event:  E = Exercised
  Principles  -> event:   E = Embodies

Run:  python -m scripts.build_safe   (writes app/seed_data/safe-essential.json)
"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "app", "seed_data", "safe-essential.json")

# --- Framework config -------------------------------------------------------
CONFIG = {
    "types": [
        {"key": "event", "label": "Events & Ceremonies", "color": "#0B2545", "kind": "container", "zone": "top", "order": 1},
        {"key": "activity", "label": "Activities", "color": "#3D5A80", "kind": "hub", "zone": "center", "order": 2},
        {"key": "role", "label": "Roles", "color": "#C9A227", "kind": "node", "code_group": "role", "zone": "left", "order": 3},
        {"key": "competency", "label": "Core Competencies", "color": "#2E7D5B", "kind": "node", "code_group": "competency", "zone": "right", "order": 4},
        {"key": "artifact", "label": "Artifacts", "color": "#C0392B", "kind": "node", "code_group": "artifact", "zone": "below", "order": 5},
        {"key": "principle", "label": "Lean-Agile Principles", "color": "#8E5BE0", "kind": "node", "code_group": "principle", "zone": "bottom", "order": 6},
    ],
    "codes": {
        "role": {"F": "Facilitates", "A": "Accountable", "P": "Participates", "I": "Informed"},
        "artifact": {"I": "Input", "C": "Created", "U": "Updated", "R": "Reviewed", "E": "Elaborated"},
        "competency": {"E": "Exercised"},
        "principle": {"E": "Embodies"},
    },
    "lanes": [
        {"key": "art", "label": "ART / Program (Agile Release Train)"},
        {"key": "team", "label": "Team (Agile Teams)"},
    ],
    "phases": [
        {"key": "plan", "label": "Prepare & Plan", "column": True, "header": "Prepare & PI Planning"},
        {"key": "delivery", "label": "Execute Iterations", "column": True, "header": "Execute Iterations ⟳"},
        {"key": "innovation", "label": "IP Iteration", "column": True, "header": "IP Iteration"},
        {"key": "inspect", "label": "Inspect & Adapt", "column": True, "header": "Inspect & Adapt"},
        {"key": "throughout", "label": "Throughout"},
    ],
    # SAFe is cyclic, not a project that ends — override the linear "Start … Close"
    # framing the Lifecycle page uses for PRINCE2/MSP.
    "lifecycle_noun": "Program Increment",
    "timeline": {
        "start_label": "PI Start",
        "end_label": "Inspect & Adapt",
        "intro": (
            "Time flows left to right across a Program Increment (PI) — a fixed timebox of "
            "roughly 8–12 weeks that repeats. Each swimlane is a level of the Agile Release "
            "Train; an event sits where it runs in the PI cadence. Iterations repeat until the "
            "PI closes with Inspect & Adapt, then the next PI begins. Click any event to see "
            "its activities in sequence."
        ),
    },
    # Worked-example documents (the "Helios" sample), keyed by the exact artifact
    # entity name; the value is a bundled PDF path relative to the SPA base
    # (frontend/public/examples/safe/*.pdf). Drives the detail panel's "View worked
    # example" button. Team Backlog and Stories intentionally share one combined
    # library document (SAFE-18). Roadmap and ART Backlog have no matching document
    # (they are living backlogs, not templates) and are left without a button.
    "examples": {
        "Vision": "examples/safe/solution-vision.pdf",
        "Features": "examples/safe/feature-definition.pdf",
        "Enablers": "examples/safe/architectural-runway-and-enabler-backlog.pdf",
        "Team Backlog": "examples/safe/team-backlog-and-user-story-template.pdf",
        "Stories": "examples/safe/team-backlog-and-user-story-template.pdf",
        "PI Objectives": "examples/safe/pi-objectives.pdf",
        "ART Planning Board": "examples/safe/program-board-and-dependency-register.pdf",
        "Iteration Goals": "examples/safe/iteration-planning-and-review-record.pdf",
        "Integrated Increment": "examples/safe/system-demo-pack.pdf",
    },
}

# --- Events (containers) — confirmed SAFe vocabulary; descriptions paraphrased --
# (code, name, lane, phase, sequence, repeats, description)
EVENTS = [
    ("PREP", "Prepare for PI Planning", "art", "plan", 1, False,
     "Establish organizational, content and logistical readiness so the ART can plan the next PI: refine the vision and roadmap, prepare and prioritize top features, and confirm scope, cadence and team capacity."),
    ("PIP", "PI Planning", "art", "plan", 2, False,
     "The cadence-based, face-to-face (or virtual) event where the whole ART plans the next Program Increment, aligning teams to a shared mission through a set of PI Objectives and a program board."),
    ("ITER", "Iteration Execution", "team", "delivery", 3, True,
     "Each iteration, teams plan, build, integrate, test and demonstrate a working increment, managing flow and refining the backlog toward their iteration goals and PI Objectives."),
    ("SD", "System Demo", "art", "delivery", 4, True,
     "At the end of every iteration the ART demonstrates the full, integrated system to stakeholders to gain objective, working-system feedback on progress toward the PI."),
    ("SYNC", "ART Sync", "art", "delivery", 5, True,
     "Recurring coordination — Coach Sync plus PO Sync — that keeps the train aligned on progress, dependencies, risks, scope and priorities between planning events."),
    ("IP", "IP Iteration", "art", "innovation", 6, False,
     "The Innovation and Planning iteration: a cadence-based buffer for innovation, continuing education and community building, plus time for PI Planning and Inspect & Adapt."),
    ("IA", "Inspect & Adapt", "art", "inspect", 7, False,
     "The significant event at the end of each PI where the ART demonstrates and evaluates the full solution, reviews metrics, and improves through a structured problem-solving workshop."),
    ("CDP", "Continuous Delivery Pipeline", "art", "throughout", None, False,
     "The continuous workflow — Continuous Exploration, Continuous Integration, Continuous Deployment and Release on Demand — through which the ART explores, builds and releases value on demand across the whole PI."),
]

# --- Roles (confirmed Essential-SAFe vocabulary) ----------------------------
ROLES = [
    "Release Train Engineer",
    "Product Management",
    "System Architect / Engineer",
    "Business Owners",
    "Scrum Master / Team Coach",
    "Product Owner",
    "Agile Team",
    "Customer",
]

# --- The 4 Essential-SAFe core competencies ---------------------------------
COMPETENCIES = [
    "Lean-Agile Leadership",
    "Team and Technical Agility",
    "Agile Product Delivery",
    "Continuous Learning Culture",
]

# --- The 10 SAFe Lean-Agile Principles --------------------------------------
PRINCIPLES = [
    "1. Take an economic view",
    "2. Apply systems thinking",
    "3. Assume variability; preserve options",
    "4. Build incrementally with fast, integrated learning cycles",
    "5. Base milestones on objective evaluation of working systems",
    "6. Make value flow without interruptions",
    "7. Apply cadence, synchronize with cross-domain planning",
    "8. Unlock the intrinsic motivation of knowledge workers",
    "9. Decentralize decision-making",
    "10. Organize around value",
]
# short handles so ACTS reference principles without retyping (and typos fail loudly)
P = {int(name.split(".")[0]): name for name in PRINCIPLES}
# competency short handles
LAL, TTA, APD, CLC = COMPETENCIES

# --- Artifacts (confirmed vocabulary) -> reconstruction confidence ----------
ARTIFACTS = {
    "Vision": "confirmed",
    "Roadmap": "confirmed",
    "ART Backlog": "confirmed",
    "Features": "confirmed",
    "Enablers": "confirmed",
    "Team Backlog": "confirmed",
    "Stories": "confirmed",
    "PI Objectives": "confirmed",
    "ART Planning Board": "confirmed",
    "Iteration Goals": "confirmed",
    "Integrated Increment": "confirmed",
}

# --- Activities (INDICATIVE reconstruction) ---------------------------------
# Each: (event_code, activity_name, roles{}, artifacts{}, [competencies], [principles])
ACTS = [
    # --- PREP: Prepare for PI Planning (ART) ---
    ("PREP", "Refine and prioritize the ART Backlog",
     {"Product Management": "A", "System Architect / Engineer": "P", "Product Owner": "P"},
     {"ART Backlog": "U", "Features": "E"}, [APD], [P[10]]),
    ("PREP", "Update the vision and roadmap",
     {"Product Management": "A", "System Architect / Engineer": "P", "Business Owners": "I"},
     {"Vision": "U", "Roadmap": "U"}, [APD], [P[1]]),
    ("PREP", "Set PI Planning scope, cadence and logistics",
     {"Release Train Engineer": "F", "Product Management": "P"},
     {"Roadmap": "R"}, [LAL], [P[7]]),
    ("PREP", "Confirm team capacity and readiness",
     {"Release Train Engineer": "F", "Scrum Master / Team Coach": "P", "Agile Team": "P"},
     {"Team Backlog": "R"}, [TTA], [P[9]]),

    # --- PIP: PI Planning (ART) ---
    ("PIP", "Present business context and vision",
     {"Business Owners": "P", "Product Management": "F", "Customer": "I"},
     {"Vision": "I", "Roadmap": "I"}, [LAL], [P[1]]),
    ("PIP", "Present architecture vision and development practices",
     {"System Architect / Engineer": "A", "Release Train Engineer": "F"},
     {"Enablers": "I", "ART Backlog": "I"}, [TTA], [P[2]]),
    ("PIP", "Team breakouts: plan iterations and draft objectives",
     {"Agile Team": "A", "Product Owner": "P", "Scrum Master / Team Coach": "F"},
     {"Team Backlog": "E", "Stories": "C", "Iteration Goals": "C", "PI Objectives": "C"},
     [APD], [P[4]]),
    ("PIP", "Coordinate dependencies and risks on the planning board",
     {"Release Train Engineer": "F", "Product Management": "P", "System Architect / Engineer": "P"},
     {"ART Planning Board": "C", "Features": "E"}, [LAL], [P[7]]),
    ("PIP", "Conduct management review and problem-solving",
     {"Business Owners": "A", "Release Train Engineer": "F", "Product Management": "P"},
     {"PI Objectives": "R"}, [LAL], [P[9]]),
    ("PIP", "Assign business value and hold the confidence vote",
     {"Business Owners": "A", "Agile Team": "P", "Release Train Engineer": "F"},
     {"PI Objectives": "C", "ART Planning Board": "U"}, [CLC], [P[8]]),

    # --- ITER: Iteration Execution (Team) ---
    ("ITER", "Plan the iteration",
     {"Product Owner": "A", "Scrum Master / Team Coach": "F", "Agile Team": "P"},
     {"Team Backlog": "I", "Stories": "E", "Iteration Goals": "C"}, [TTA], [P[7]]),
    ("ITER", "Synchronize daily and manage flow",
     {"Scrum Master / Team Coach": "F", "Agile Team": "A"},
     {"Team Backlog": "U"}, [TTA], [P[6]]),
    ("ITER", "Build, integrate and test the increment",
     {"Agile Team": "A", "System Architect / Engineer": "P"},
     {"Stories": "U", "Enablers": "U", "Integrated Increment": "C"}, [TTA], [P[4]]),
    ("ITER", "Refine the team backlog",
     {"Product Owner": "A", "Agile Team": "P"},
     {"Team Backlog": "U", "Stories": "E"}, [APD], [P[3]]),
    ("ITER", "Review and retrospect the iteration",
     {"Scrum Master / Team Coach": "F", "Product Owner": "P", "Agile Team": "P"},
     {"Iteration Goals": "R", "Integrated Increment": "R"}, [CLC], [P[5]]),

    # --- SD: System Demo (ART) ---
    ("SD", "Integrate the full system for demo",
     {"System Architect / Engineer": "A", "Agile Team": "P"},
     {"Integrated Increment": "U"}, [TTA], [P[5]]),
    ("SD", "Demonstrate integrated value to stakeholders",
     {"Product Management": "F", "Business Owners": "P", "Customer": "P"},
     {"Integrated Increment": "R", "Features": "R"}, [APD], [P[5]]),
    ("SD", "Capture feedback and adjust the ART Backlog",
     {"Product Management": "A", "Product Owner": "P"},
     {"ART Backlog": "U", "Features": "E"}, [APD], [P[3]]),

    # --- SYNC: ART Sync (ART) ---
    ("SYNC", "Coach Sync: track progress and impediments",
     {"Release Train Engineer": "F", "Scrum Master / Team Coach": "A"},
     {"ART Planning Board": "U"}, [LAL], [P[6]]),
    ("SYNC", "PO Sync: align scope, priorities and dependencies",
     {"Product Management": "F", "Product Owner": "A"},
     {"ART Backlog": "U", "Features": "E", "PI Objectives": "R"}, [APD], [P[9]]),
    ("SYNC", "Escalate and resolve cross-team risks",
     {"Release Train Engineer": "A", "System Architect / Engineer": "P", "Business Owners": "I"},
     {"ART Planning Board": "U"}, [LAL], [P[2]]),

    # --- IP: IP Iteration (ART) ---
    ("IP", "Innovate and spike",
     {"Agile Team": "A", "System Architect / Engineer": "P"},
     {"Enablers": "C"}, [CLC], [P[8]]),
    ("IP", "Continue education and grow communities of practice",
     {"Scrum Master / Team Coach": "F", "Agile Team": "P"},
     {}, [CLC], [P[8]]),
    ("IP", "Provide estimating and planning buffer",
     {"Release Train Engineer": "F", "Product Owner": "P"},
     {"Team Backlog": "U", "PI Objectives": "R"}, [LAL], [P[7]]),

    # --- IA: Inspect & Adapt (ART) ---
    ("IA", "Demonstrate and evaluate the full PI solution",
     {"Product Management": "F", "System Architect / Engineer": "P", "Business Owners": "P", "Customer": "I"},
     {"Integrated Increment": "R", "PI Objectives": "R"}, [APD], [P[5]]),
    ("IA", "Review quantitative and qualitative metrics",
     {"Release Train Engineer": "F", "Business Owners": "P"},
     {"PI Objectives": "R"}, [CLC], [P[1]]),
    ("IA", "Facilitate the problem-solving workshop",
     {"Release Train Engineer": "A", "Agile Team": "P", "Scrum Master / Team Coach": "P"},
     {"ART Backlog": "U"}, [CLC], [P[2]]),
    ("IA", "Create improvement backlog items",
     {"Product Management": "A", "Agile Team": "P"},
     {"ART Backlog": "U", "Team Backlog": "U"}, [CLC], [P[4]]),

    # --- CDP: Continuous Delivery Pipeline (ART, throughout) ---
    ("CDP", "Continuous Exploration: understand customer needs",
     {"Product Management": "A", "Customer": "P", "System Architect / Engineer": "P"},
     {"ART Backlog": "E", "Features": "C", "Vision": "R"}, [APD], [P[10]]),
    ("CDP", "Continuous Integration: build and test continuously",
     {"Agile Team": "A", "System Architect / Engineer": "P"},
     {"Stories": "U", "Enablers": "U", "Integrated Increment": "U"}, [TTA], [P[4]]),
    ("CDP", "Continuous Deployment: deploy to production",
     {"Agile Team": "A", "Release Train Engineer": "P", "System Architect / Engineer": "P"},
     {"Integrated Increment": "U"}, [APD], [P[6]]),
    ("CDP", "Release on Demand: release value to customers",
     {"Product Management": "A", "Business Owners": "P", "Customer": "I"},
     {"Integrated Increment": "R", "Features": "R"}, [APD], [P[10]]),
]

EVENT_NAME = {code: name for code, name, *_ in EVENTS}


def build():
    entities = []
    relationships = []

    def ent(**kw):
        base = {"code": None, "subgroup": None, "parent": None, "confidence": "confirmed",
                "description": None, "sort_order": 0, "lifecycle_level": None,
                "lifecycle_phase": None, "sequence": None, "repeats": False}
        base.update(kw)
        entities.append(base)

    # events (containers)
    for i, (code, name, lane, phase, seq, repeats, desc) in enumerate(EVENTS, 1):
        ent(type="event", name=name, code=code, confidence="confirmed", description=desc,
            sort_order=i, lifecycle_level=lane, lifecycle_phase=phase, sequence=seq, repeats=repeats)
    # roles / competencies / principles (confirmed vocabulary)
    for i, r in enumerate(ROLES, 1):
        ent(type="role", name=r, sort_order=i)
    for i, c in enumerate(COMPETENCIES, 1):
        ent(type="competency", name=c, sort_order=i)
    for i, pr in enumerate(PRINCIPLES, 1):
        ent(type="principle", name=pr, sort_order=i)
    for i, (art, conf) in enumerate(ARTIFACTS.items(), 1):
        ent(type="artifact", name=art, confidence=conf, sort_order=i)

    # validate references up front so a typo fails the build, not silently drops
    valid_roles, valid_arts = set(ROLES), set(ARTIFACTS)
    valid_comps, valid_prins = set(COMPETENCIES), set(PRINCIPLES)

    # activities + relationships (indicative)
    order_by_event = {}
    for (ecode, aname, roles, arts, comps, prins) in ACTS:
        ename = EVENT_NAME[ecode]
        order_by_event[ecode] = order_by_event.get(ecode, 0) + 1
        ent(type="activity", name=aname, parent=f"event::{ename}",
            confidence="indicative", sort_order=order_by_event[ecode])
        src = f"activity::{aname}"
        for role, c in roles.items():
            assert role in valid_roles, f"unknown role {role!r} in {aname!r}"
            relationships.append({"from": src, "to": f"role::{role}", "code": c, "confidence": "indicative"})
        for art, c in arts.items():
            assert art in valid_arts, f"unknown artifact {art!r} in {aname!r}"
            relationships.append({"from": src, "to": f"artifact::{art}", "code": c, "confidence": "indicative"})
        for comp in comps:
            assert comp in valid_comps, f"unknown competency {comp!r} in {aname!r}"
            relationships.append({"from": src, "to": f"competency::{comp}", "code": "E", "confidence": "indicative"})
        for pr in prins:
            assert pr in valid_prins, f"unknown principle {pr!r} in {aname!r}"
            relationships.append({"from": src, "to": f"principle::{pr}", "code": "E", "confidence": "indicative"})

    doc = {
        "framework": {
            "key": "safe-essential",
            "name": "SAFe",
            "edition": "6.0 — Essential configuration (Scaled Agile Framework)",
            "description": (
                "SAFe 6.0 Essential Method Map: the core Agile Release Train and Team events, "
                "laid out across the PI (Program Increment) cadence and cross-referenced to "
                "roles, artifacts, the 4 Essential core competencies and the 10 Lean-Agile "
                "Principles. Role codes: F=Facilitates, A=Accountable, P=Participates, "
                "I=Informed. Artifact codes: I=Input, C=Created, U=Updated, R=Reviewed, "
                "E=Elaborated. Scope is Essential SAFe (Team + ART); Portfolio and Large "
                "Solution levels are out of scope for this map. The activity breakdown of each "
                "event and every cross-reference mark are an indicative, best-effort "
                "reconstruction of the SAFe model and must be SME-verified against the licensed "
                "SAFe body of knowledge before formal use. SAFe® and Scaled Agile Framework® "
                "are trademarks of Scaled Agile, Inc.; this is an independent reference tool, "
                "not affiliated with or endorsed by Scaled Agile, Inc."
            ),
            "sort_order": 3,
            "config": CONFIG,
        },
        "entities": entities,
        "relationships": relationships,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"Wrote {os.path.abspath(OUT)}")
    print(f"  entities: {len(entities)}  relationships: {len(relationships)}")
    print("  by type:", dict(Counter(e["type"] for e in entities)))


if __name__ == "__main__":
    build()
