"""Build seed_data/pmbok-6.json for the PMBOK Guide (6th edition) Method Map.

Like build_msp.py / build_safe.py this holds the data inline (no source
spreadsheet). PMBOK 6 is the classic **process matrix**: 49 processes arranged in
a grid of 5 Process Groups (columns) x 10 Knowledge Areas (rows). We render that
grid faithfully (Option 2): the Knowledge Area is the **container**, the process
is the **hub** (it carries the cross-references), and each process self-places at
its (KA row, Process Group column) cell in the Lifecycle view.

The **5 Process Groups, 10 Knowledge Areas and the 49 processes and their grid
placement are confirmed, widely-published PMBOK 6 facts**. The **ITTO
cross-references (which Inputs / Tools & Techniques / Outputs each process uses)
are a curated, INDICATIVE reconstruction** — the most characteristic items per
process, not the guide's exhaustive tables — and must be SME-verified against the
licensed PMBOK Guide before formal use. No PMI copyrighted text is reproduced;
only process / artifact / tool names and cross-reference marks.

Codes:
  Artifacts (Inputs & Outputs):  I = Input   O = Output
  Tools & Techniques:            T = Tool / Technique

PMBOK, PMI and PMP are marks of the Project Management Institute, Inc. This is an
independent reference tool, not affiliated with or endorsed by PMI.

Run:  python -m scripts.build_pmbok   (writes app/seed_data/pmbok-6.json)
"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "app", "seed_data", "pmbok-6.json")

# --- Process Groups (the 5 timeline columns) --------------------------------
PGS = [
    ("initiating", "Initiating"),
    ("planning", "Planning"),
    ("executing", "Executing"),
    ("mc", "Monitoring & Controlling"),
    ("closing", "Closing"),
]

# --- Knowledge Areas (the 10 swimlane rows / containers) --------------------
# (key, code, name, description)
KAS = [
    ("integration", "INT", "Project Integration Management",
     "Unify, consolidate and coordinate the processes and activities of project management."),
    ("scope", "SCO", "Project Scope Management",
     "Ensure the project includes all the work required, and only the work required, to complete it."),
    ("schedule", "SCH", "Project Schedule Management",
     "Manage the timely completion of the project."),
    ("cost", "COS", "Project Cost Management",
     "Plan, estimate, budget, finance, fund, manage and control costs so the project is completed within the approved budget."),
    ("quality", "QUA", "Project Quality Management",
     "Incorporate the organization's quality policy into planning, managing and controlling quality requirements."),
    ("resource", "RES", "Project Resource Management",
     "Identify, acquire and manage the resources needed for successful project completion."),
    ("communications", "COM", "Project Communications Management",
     "Ensure timely and appropriate planning, collection, distribution and management of project information."),
    ("risk", "RSK", "Project Risk Management",
     "Plan, identify, analyse, respond to, implement responses for and monitor risk on the project."),
    ("procurement", "PRO", "Project Procurement Management",
     "Purchase or acquire the products, services or results needed from outside the project team."),
    ("stakeholder", "STK", "Project Stakeholder Management",
     "Identify stakeholders, analyse their expectations and engage them appropriately in decisions and execution."),
]
KA_KEY = {code: key for key, code, *_ in KAS}

# --- The 49 processes (INDICATIVE ITTOs) ------------------------------------
# (num, name, KA-code, PG-key, inputs[], tools[], outputs[])
# num is the PMBOK section number; used as the display code and to order the grid.
PROCESSES = [
    # 4. Integration
    ("4.1", "Develop Project Charter", "INT", "initiating",
     ["Business Documents", "Agreements", "Enterprise Environmental Factors"],
     ["Expert Judgment", "Data Gathering", "Meetings"],
     ["Project Charter", "Assumption Log"]),
    ("4.2", "Develop Project Management Plan", "INT", "planning",
     ["Project Charter", "Outputs from Other Processes"],
     ["Expert Judgment", "Data Gathering", "Meetings"],
     ["Project Management Plan"]),
    ("4.3", "Direct and Manage Project Work", "INT", "executing",
     ["Project Management Plan", "Approved Change Requests"],
     ["Expert Judgment", "Project Management Information System", "Meetings"],
     ["Deliverables", "Work Performance Data", "Issue Log", "Change Requests"]),
    ("4.4", "Manage Project Knowledge", "INT", "executing",
     ["Project Management Plan", "Deliverables", "Lessons Learned Register"],
     ["Expert Judgment", "Knowledge Management", "Information Management"],
     ["Lessons Learned Register"]),
    ("4.5", "Monitor and Control Project Work", "INT", "mc",
     ["Project Management Plan", "Work Performance Information", "Agreements"],
     ["Expert Judgment", "Data Analysis", "Decision Making", "Meetings"],
     ["Work Performance Reports", "Change Requests"]),
    ("4.6", "Perform Integrated Change Control", "INT", "mc",
     ["Project Management Plan", "Change Requests", "Work Performance Reports"],
     ["Expert Judgment", "Change Control Tools", "Decision Making", "Meetings"],
     ["Approved Change Requests", "Change Log"]),
    ("4.7", "Close Project or Phase", "INT", "closing",
     ["Project Charter", "Project Management Plan", "Accepted Deliverables", "Business Documents"],
     ["Expert Judgment", "Data Analysis", "Meetings"],
     ["Final Report", "Lessons Learned Register"]),

    # 5. Scope
    ("5.1", "Plan Scope Management", "SCO", "planning",
     ["Project Charter", "Project Management Plan"],
     ["Expert Judgment", "Data Analysis", "Meetings"],
     ["Scope Management Plan", "Requirements Management Plan"]),
    ("5.2", "Collect Requirements", "SCO", "planning",
     ["Scope Management Plan", "Stakeholder Register", "Business Documents"],
     ["Data Gathering", "Data Analysis", "Interpersonal and Team Skills"],
     ["Requirements Documentation", "Requirements Traceability Matrix"]),
    ("5.3", "Define Scope", "SCO", "planning",
     ["Project Charter", "Requirements Documentation"],
     ["Expert Judgment", "Data Analysis", "Product Analysis"],
     ["Project Scope Statement"]),
    ("5.4", "Create WBS", "SCO", "planning",
     ["Project Scope Statement", "Requirements Documentation"],
     ["Expert Judgment", "Decomposition"],
     ["Scope Baseline"]),
    ("5.5", "Validate Scope", "SCO", "mc",
     ["Verified Deliverables", "Requirements Documentation", "Work Performance Data"],
     ["Inspection", "Decision Making"],
     ["Accepted Deliverables", "Work Performance Information", "Change Requests"]),
    ("5.6", "Control Scope", "SCO", "mc",
     ["Scope Baseline", "Work Performance Data", "Requirements Documentation"],
     ["Data Analysis"],
     ["Work Performance Information", "Change Requests"]),

    # 6. Schedule
    ("6.1", "Plan Schedule Management", "SCH", "planning",
     ["Project Charter", "Project Management Plan"],
     ["Expert Judgment", "Data Analysis", "Meetings"],
     ["Schedule Management Plan"]),
    ("6.2", "Define Activities", "SCH", "planning",
     ["Schedule Management Plan", "Scope Baseline"],
     ["Decomposition", "Rolling Wave Planning", "Meetings"],
     ["Activity List", "Milestone List"]),
    ("6.3", "Sequence Activities", "SCH", "planning",
     ["Activity List", "Milestone List"],
     ["Precedence Diagramming Method", "Dependency Determination and Integration", "Leads and Lags"],
     ["Project Schedule Network Diagram"]),
    ("6.4", "Estimate Activity Durations", "SCH", "planning",
     ["Activity List", "Resource Requirements", "Resource Calendars"],
     ["Analogous Estimating", "Parametric Estimating", "Three-Point Estimating", "Bottom-Up Estimating"],
     ["Duration Estimates", "Basis of Estimates"]),
    ("6.5", "Develop Schedule", "SCH", "planning",
     ["Project Schedule Network Diagram", "Duration Estimates", "Resource Requirements"],
     ["Schedule Network Analysis", "Critical Path Method", "Resource Optimization", "Schedule Compression"],
     ["Project Schedule", "Schedule Baseline"]),
    ("6.6", "Control Schedule", "SCH", "mc",
     ["Schedule Baseline", "Project Schedule", "Work Performance Data"],
     ["Data Analysis", "Critical Path Method", "Project Management Information System"],
     ["Work Performance Information", "Schedule Forecasts", "Change Requests"]),

    # 7. Cost
    ("7.1", "Plan Cost Management", "COS", "planning",
     ["Project Charter", "Project Management Plan"],
     ["Expert Judgment", "Data Analysis", "Meetings"],
     ["Cost Management Plan"]),
    ("7.2", "Estimate Costs", "COS", "planning",
     ["Cost Management Plan", "Scope Baseline", "Project Schedule"],
     ["Analogous Estimating", "Parametric Estimating", "Bottom-Up Estimating", "Reserve Analysis"],
     ["Cost Estimates", "Basis of Estimates"]),
    ("7.3", "Determine Budget", "COS", "planning",
     ["Cost Estimates", "Scope Baseline", "Project Schedule"],
     ["Cost Aggregation", "Reserve Analysis", "Funding Limit Reconciliation"],
     ["Cost Baseline", "Project Funding Requirements"]),
    ("7.4", "Control Costs", "COS", "mc",
     ["Cost Baseline", "Work Performance Data", "Project Funding Requirements"],
     ["Earned Value Analysis", "Reserve Analysis", "Trend Analysis"],
     ["Work Performance Information", "Cost Forecasts", "Change Requests"]),

    # 8. Quality
    ("8.1", "Plan Quality Management", "QUA", "planning",
     ["Project Management Plan", "Requirements Documentation", "Stakeholder Register"],
     ["Data Gathering", "Data Analysis", "Data Representation", "Meetings"],
     ["Quality Management Plan", "Quality Metrics"]),
    ("8.2", "Manage Quality", "QUA", "executing",
     ["Quality Management Plan", "Quality Metrics", "Quality Control Measurements"],
     ["Data Analysis", "Audits", "Design for X", "Data Representation"],
     ["Quality Report", "Test and Evaluation Documents", "Change Requests"]),
    ("8.3", "Control Quality", "QUA", "mc",
     ["Quality Management Plan", "Quality Metrics", "Deliverables", "Work Performance Data"],
     ["Data Gathering", "Inspection", "Testing/Product Evaluations", "Data Representation"],
     ["Quality Control Measurements", "Verified Deliverables", "Work Performance Information"]),

    # 9. Resource
    ("9.1", "Plan Resource Management", "RES", "planning",
     ["Project Charter", "Project Management Plan", "Requirements Documentation"],
     ["Expert Judgment", "Data Representation", "Meetings"],
     ["Resource Management Plan", "Team Charter"]),
    ("9.2", "Estimate Activity Resources", "RES", "planning",
     ["Resource Management Plan", "Activity List", "Cost Estimates"],
     ["Analogous Estimating", "Parametric Estimating", "Bottom-Up Estimating"],
     ["Resource Requirements", "Resource Breakdown Structure", "Basis of Estimates"]),
    ("9.3", "Acquire Resources", "RES", "executing",
     ["Resource Management Plan", "Resource Requirements"],
     ["Decision Making", "Interpersonal and Team Skills", "Pre-Assignment", "Virtual Teams"],
     ["Physical Resource Assignments", "Project Team Assignments", "Resource Calendars"]),
    ("9.4", "Develop Team", "RES", "executing",
     ["Project Team Assignments", "Team Charter", "Resource Calendars"],
     ["Colocation", "Virtual Teams", "Recognition and Rewards", "Training", "Team Building"],
     ["Team Performance Assessments", "Change Requests"]),
    ("9.5", "Manage Team", "RES", "executing",
     ["Project Team Assignments", "Team Performance Assessments", "Work Performance Reports"],
     ["Interpersonal and Team Skills", "Conflict Management", "Decision Making"],
     ["Change Requests"]),
    ("9.6", "Control Resources", "RES", "mc",
     ["Resource Management Plan", "Physical Resource Assignments", "Work Performance Data"],
     ["Data Analysis", "Problem Solving", "Negotiation"],
     ["Work Performance Information", "Change Requests"]),

    # 10. Communications
    ("10.1", "Plan Communications Management", "COM", "planning",
     ["Project Charter", "Project Management Plan", "Stakeholder Register"],
     ["Communication Requirements Analysis", "Communication Technology", "Communication Models", "Communication Methods"],
     ["Communications Management Plan"]),
    ("10.2", "Manage Communications", "COM", "executing",
     ["Communications Management Plan", "Work Performance Reports"],
     ["Communication Technology", "Communication Methods", "Interpersonal and Team Skills"],
     ["Project Communications"]),
    ("10.3", "Monitor Communications", "COM", "mc",
     ["Communications Management Plan", "Project Communications", "Work Performance Data"],
     ["Expert Judgment", "Data Analysis", "Meetings"],
     ["Work Performance Information", "Change Requests"]),

    # 11. Risk
    ("11.1", "Plan Risk Management", "RSK", "planning",
     ["Project Charter", "Project Management Plan", "Stakeholder Register"],
     ["Expert Judgment", "Data Analysis", "Meetings"],
     ["Risk Management Plan"]),
    ("11.2", "Identify Risks", "RSK", "planning",
     ["Risk Management Plan", "Requirements Documentation", "Cost Estimates", "Duration Estimates"],
     ["Data Gathering", "Data Analysis", "Interpersonal and Team Skills"],
     ["Risk Register", "Risk Report"]),
    ("11.3", "Perform Qualitative Risk Analysis", "RSK", "planning",
     ["Risk Management Plan", "Risk Register", "Stakeholder Register"],
     ["Data Analysis", "Risk Categorization", "Probability and Impact Matrix", "Data Representation"],
     ["Risk Register", "Risk Report"]),
    ("11.4", "Perform Quantitative Risk Analysis", "RSK", "planning",
     ["Risk Management Plan", "Risk Register", "Cost Baseline"],
     ["Data Analysis", "Representations of Uncertainty", "Simulation"],
     ["Risk Report"]),
    ("11.5", "Plan Risk Responses", "RSK", "planning",
     ["Risk Management Plan", "Risk Register", "Risk Report"],
     ["Strategies for Threats", "Strategies for Opportunities", "Contingent Response Strategies", "Decision Making"],
     ["Change Requests", "Risk Register", "Risk Report"]),
    ("11.6", "Implement Risk Responses", "RSK", "executing",
     ["Risk Management Plan", "Risk Register", "Risk Report"],
     ["Expert Judgment", "Interpersonal and Team Skills", "Project Management Information System"],
     ["Change Requests"]),
    ("11.7", "Monitor Risks", "RSK", "mc",
     ["Risk Management Plan", "Risk Register", "Work Performance Data", "Work Performance Reports"],
     ["Data Analysis", "Audits", "Meetings"],
     ["Work Performance Information", "Change Requests"]),

    # 12. Procurement
    ("12.1", "Plan Procurement Management", "PRO", "planning",
     ["Project Charter", "Business Documents", "Requirements Documentation"],
     ["Expert Judgment", "Data Gathering", "Source Selection Analysis", "Meetings"],
     ["Procurement Management Plan", "Procurement Strategy", "Bid Documents", "Source Selection Criteria"]),
    ("12.2", "Conduct Procurements", "PRO", "executing",
     ["Procurement Management Plan", "Bid Documents", "Seller Proposals"],
     ["Expert Judgment", "Advertising", "Bidder Conferences", "Proposal Evaluation"],
     ["Selected Sellers", "Agreements", "Change Requests"]),
    ("12.3", "Control Procurements", "PRO", "mc",
     ["Agreements", "Procurement Management Plan", "Work Performance Data"],
     ["Claims Administration", "Data Analysis", "Inspection", "Audits"],
     ["Closed Procurements", "Work Performance Information", "Change Requests"]),

    # 13. Stakeholder
    ("13.1", "Identify Stakeholders", "STK", "initiating",
     ["Project Charter", "Business Documents", "Agreements"],
     ["Expert Judgment", "Data Gathering", "Data Analysis", "Stakeholder Mapping/Representation"],
     ["Stakeholder Register", "Change Requests"]),
    ("13.2", "Plan Stakeholder Engagement", "STK", "planning",
     ["Project Charter", "Project Management Plan", "Stakeholder Register"],
     ["Expert Judgment", "Data Analysis", "Decision Making", "Data Representation"],
     ["Stakeholder Engagement Plan"]),
    ("13.3", "Manage Stakeholder Engagement", "STK", "executing",
     ["Stakeholder Engagement Plan", "Communications Management Plan", "Change Log"],
     ["Communication Skills", "Interpersonal and Team Skills", "Ground Rules", "Meetings"],
     ["Change Requests"]),
    ("13.4", "Monitor Stakeholder Engagement", "STK", "mc",
     ["Stakeholder Engagement Plan", "Work Performance Data", "Project Communications"],
     ["Data Analysis", "Decision Making", "Data Representation"],
     ["Work Performance Information", "Change Requests"]),
]

# Artifacts (Inputs/Outputs) and Tools are the union of what the processes use;
# every referenced name becomes one node. Names are confirmed PMBOK vocabulary.


def build():
    entities = []
    relationships = []

    def ent(**kw):
        base = {"code": None, "subgroup": None, "parent": None, "confidence": "confirmed",
                "description": None, "sort_order": 0, "lifecycle_level": None,
                "lifecycle_phase": None, "sequence": None, "repeats": False}
        base.update(kw)
        entities.append(base)

    # Knowledge Areas (containers)
    for i, (key, code, name, desc) in enumerate(KAS, 1):
        ent(type="knowledge-area", name=name, code=code, confidence="confirmed",
            description=desc, sort_order=i)

    # collect artifact + tool catalogs from the process ITTOs
    artifacts, tools = {}, {}
    for (num, name, ka, pg, inputs, tls, outputs) in PROCESSES:
        for a in inputs + outputs:
            artifacts.setdefault(a, True)
        for t in tls:
            tools.setdefault(t, True)

    for i, a in enumerate(sorted(artifacts), 1):
        ent(type="artifact", name=a, confidence="confirmed", sort_order=i)
    for i, t in enumerate(sorted(tools), 1):
        ent(type="tool", name=t, confidence="confirmed", sort_order=i)

    # Processes (hubs) + ITTO relationships (indicative)
    ka_name = {code: name for key, code, name, *_ in KAS}
    seq = 0
    order_by_ka = {}
    for (num, name, ka, pg, inputs, tls, outputs) in PROCESSES:
        seq += 1
        order_by_ka[ka] = order_by_ka.get(ka, 0) + 1
        ent(type="process", name=name, code=num, parent=f"knowledge-area::{ka_name[ka]}",
            confidence="confirmed",
            description=f"{ka_name[ka]} — {PG_LABEL[pg]} process.",
            sort_order=seq, lifecycle_level=KA_KEY[ka], lifecycle_phase=pg, sequence=seq)
        src = f"process::{name}"
        for a in inputs:
            relationships.append({"from": src, "to": f"artifact::{a}", "code": "I", "confidence": "indicative"})
        for t in tls:
            relationships.append({"from": src, "to": f"tool::{t}", "code": "T", "confidence": "indicative"})
        for a in outputs:
            relationships.append({"from": src, "to": f"artifact::{a}", "code": "O", "confidence": "indicative"})

    config = {
        "types": [
            {"key": "knowledge-area", "label": "Knowledge Areas", "color": "#0B2545", "kind": "container", "zone": "top", "order": 1},
            {"key": "process", "label": "Processes", "color": "#3D5A80", "kind": "hub", "zone": "center", "order": 2},
            {"key": "artifact", "label": "Inputs & Outputs", "color": "#C0392B", "kind": "node", "code_group": "io", "zone": "below", "order": 3},
            {"key": "tool", "label": "Tools & Techniques", "color": "#2E7D5B", "kind": "node", "code_group": "tool", "zone": "below", "order": 4, "label_below": True},
        ],
        "codes": {
            "io": {"I": "Input", "O": "Output"},
            "tool": {"T": "Tool / Technique"},
        },
        # 10 Knowledge Areas = swimlane rows; 5 Process Groups = timeline columns.
        "lanes": [{"key": key, "label": name} for key, code, name, *_ in KAS],
        "phases": [{"key": k, "label": lbl, "column": True, "header": lbl} for k, lbl in PGS],
        # Option 2: the Lifecycle/grid view renders the HUB layer (processes) placed
        # at (lifecycle_level = KA row, lifecycle_phase = Process Group column) — the
        # iconic PMBOK 10x5 process matrix — rather than the container layer.
        "lifecycle_layer": "hub",
        "lifecycle_noun": "process matrix",
        "timeline": {
            "heading": "PMBOK 6 — the 49-process matrix (5 Process Groups × 10 Knowledge Areas)",
            "start_label": "Initiating",
            "end_label": "Closing",
            "intro": (
                "The PMBOK process matrix: 49 processes arranged in a grid of 5 Process "
                "Groups (columns, left to right: Initiating → Planning → Executing → "
                "Monitoring & Controlling → Closing) across 10 Knowledge Areas (rows). Each "
                "cell holds the processes at that intersection. Click any process to open it "
                "in the graph and see its Inputs, Tools & Techniques and Outputs."
            ),
        },
    }

    doc = {
        "framework": {
            "key": "pmbok-6",
            "name": "PMBOK",
            "edition": "6th edition (A Guide to the Project Management Body of Knowledge, 2017)",
            "description": (
                "PMBOK Guide 6th-edition Method Map: the 49 project-management processes laid "
                "out in the classic matrix of 5 Process Groups x 10 Knowledge Areas, "
                "cross-referenced to their Inputs, Tools & Techniques and Outputs (ITTOs). "
                "Codes: I=Input, O=Output (artifacts), T=Tool/Technique. The Process Groups, "
                "Knowledge Areas and the 49 processes and their grid placement are confirmed "
                "PMBOK facts; the ITTO cross-references are a curated, indicative "
                "reconstruction (the most characteristic items per process, not the guide's "
                "exhaustive tables) and must be SME-verified against the licensed PMBOK Guide "
                "before formal use. PMBOK, PMI and PMP are marks of the Project Management "
                "Institute, Inc.; this is an independent reference tool, not affiliated with "
                "or endorsed by PMI."
            ),
            "sort_order": 4,
            "config": config,
        },
        "entities": entities,
        "relationships": relationships,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"Wrote {os.path.abspath(OUT)}")
    print(f"  entities: {len(entities)}  relationships: {len(relationships)}")
    print("  by type:", dict(Counter(e["type"] for e in entities)))
    # sanity: every process placed in a valid (KA, PG) cell
    pgs = {k for k, _ in PGS}
    kas = {key for key, *_ in KAS}
    for e in entities:
        if e["type"] == "process":
            assert e["lifecycle_phase"] in pgs, e
            assert e["lifecycle_level"] in kas, e
    print(f"  grid: {len(PROCESSES)} processes across {len(kas)} KAs x {len(pgs)} Process Groups")


PG_LABEL = {k: lbl for k, lbl in PGS}

if __name__ == "__main__":
    build()
