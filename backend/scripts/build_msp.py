"""Build seed_data/msp-5.json for the MSP (Managing Successful Programmes,
5th edition) Method Map.

Unlike extract_prince2.py (which reads a cross-reference spreadsheet), this file
holds the MSP data inline: the framework structure is confirmed MSP vocabulary,
but the ACTIVITY breakdown and every cross-reference mark are an **indicative,
best-effort reconstruction** of the 5th-edition model — to be SME-verified
against the licensed manual before formal use. No manual text is reproduced; only
activity names and cross-reference marks. Codes follow the user's MSP sheet:
  Roles & Themes:  C = Responsible   P = Related   N = Assists
  Products:  CO = Confirmed  CR = Created  RF = Refined  RV = Reviewed
             UP = Updated    IM = Implemented
  Principles:  E = Embodies (indicative link from the activities that most
               exemplify each principle)

Run:  python -m scripts.build_msp   (writes app/seed_data/msp-5.json)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "app", "seed_data", "msp-5.json")

# --- Framework config -------------------------------------------------------
CONFIG = {
    "types": [
        {"key": "process", "label": "Programme Processes", "color": "#0B2545", "kind": "container", "zone": "top", "order": 1},
        {"key": "activity", "label": "Activities", "color": "#3D5A80", "kind": "hub", "zone": "center", "order": 2},
        {"key": "role", "label": "Roles", "color": "#C9A227", "kind": "node", "code_group": "role", "zone": "left", "order": 3},
        {"key": "theme", "label": "Themes", "color": "#2E7D5B", "kind": "node", "code_group": "role", "zone": "right", "order": 4},
        {"key": "product", "label": "Products", "color": "#C0392B", "kind": "node", "code_group": "product", "zone": "below", "order": 5},
        {"key": "principle", "label": "Principles", "color": "#8E5BE0", "kind": "node", "code_group": "principle", "zone": "bottom", "order": 6},
    ],
    "codes": {
        "role": {"C": "Responsible", "P": "Related", "N": "Assists"},
        "product": {"CO": "Confirmed", "CR": "Created", "RF": "Refined", "RV": "Reviewed", "UP": "Updated", "IM": "Implemented"},
        "principle": {"E": "Embodies"},
    },
    "lanes": [
        {"key": "sponsoring", "label": "Sponsoring (SRO / Sponsoring Group)"},
        {"key": "managing", "label": "Managing (Programme Manager / Office)"},
        {"key": "delivering", "label": "Delivering (Business Change)"},
    ],
    "phases": [
        {"key": "identify", "label": "Identify", "column": True, "header": "Identify"},
        {"key": "definition", "label": "Definition (Design & Plan)", "column": True, "header": "Definition"},
        {"key": "delivery", "label": "Delivery tranches", "column": True, "header": "Delivery ⟳"},
        {"key": "close", "label": "Close", "column": True, "header": "Close"},
        {"key": "throughout", "label": "Throughout"},
    ],
    # Worked-example documents (the "Helios" sample programme), keyed by the exact
    # product entity name; the value is a bundled PDF path relative to the SPA base
    # (frontend/public/examples/msp/*.pdf). Drives the detail panel's "View worked
    # example" button. Sourced from the PMO Template Library. Five MSP products have
    # no matching library document (Organisation Structure & RACI, Tranche / Stage
    # Plan, Lessons Log, Audit / Assurance Log, Programme Board Decision Log) and are
    # intentionally left without a button rather than mapped to a loose approximation.
    "examples": {
        "Vision Statement": "examples/msp/vision-statement.pdf",
        "Target Operating Model": "examples/msp/target-operating-model.pdf",
        "Business Case": "examples/msp/programme-business-case.pdf",
        "Benefit Profile(s)": "examples/msp/benefit-profile.pdf",
        "Benefits Realisation Plan": "examples/msp/benefits-realisation-plan.pdf",
        "Programme Plan": "examples/msp/programme-plan.pdf",
        "Information Mgmt Approach": "examples/msp/information-management-approach.pdf",
        "Quality & Assurance Approach": "examples/msp/assurance-approach-and-plan.pdf",
        "Risk & Issue Register": "examples/msp/programme-risk-register.pdf",
    },
}

# --- Processes (confirmed MSP vocabulary; objectives paraphrased) ------------
# (code, name, lane, phase, sequence, repeats, objective)
PROCESSES = [
    ("IP", "Identify the Programme", "sponsoring", "identify", 1, False,
     "Confirm the programme mandate and its justification, and appoint the initial leadership so the programme can be sanctioned to start."),
    ("DO", "Design the Outcomes", "managing", "definition", 2, False,
     "Shape the change: define the target operating model, the benefits and the full business case."),
    ("PP", "Plan Progressive Delivery", "managing", "definition", 3, False,
     "Plan how the change will be delivered incrementally through tranches, and set up the management approaches."),
    ("DC", "Deliver the Capabilities", "delivering", "delivery", 4, True,
     "Coordinate the projects and other work that create the capabilities the programme needs."),
    ("EO", "Embed the Outcomes", "delivering", "delivery", 5, True,
     "Transition new capabilities into business-as-usual and realize the intended benefits."),
    ("EN", "Evaluate New Information", "managing", "delivery", 6, True,
     "Review progress and new information, respond to risk and change, and decide whether to continue."),
    ("CP", "Close the Programme", "managing", "close", 7, False,
     "Confirm the outcomes and benefits, hand over ongoing realization, and disband the programme."),
]

ROLES = ["Sponsoring Group", "Senior Responsible Owner", "Programme Manager", "Business Change Manager", "Programme Office"]
THEMES = ["Organization", "Design", "Justification", "Structure", "Knowledge", "Assurance", "Decisions"]
PRINCIPLES = [
    "Lead with purpose", "Collaborate across boundaries", "Deal with ambiguity",
    "Align with priorities", "Deploy diverse skills", "Realize measurable benefits",
    "Bring pace and value",
]
# product -> confidence (from the intake 'Confirm' sheet)
PRODUCTS = {
    "Organisation Structure & RACI": "indicative",
    "Vision Statement": "indicative",
    "Target Operating Model": "confirmed",
    "Business Case": "confirmed",
    "Benefit Profile(s)": "indicative",
    "Benefits Realisation Plan": "indicative",
    "Programme Plan": "indicative",
    "Tranche / Stage Plan": "indicative",
    "Information Mgmt Approach": "indicative",
    "Lessons Log": "indicative",
    "Quality & Assurance Approach": "indicative",
    "Audit / Assurance Log": "indicative",
    "Programme Board Decision Log": "indicative",
    "Risk & Issue Register": "indicative",
}

# --- Activities (INDICATIVE reconstruction) ---------------------------------
# Each: (process_code, activity_name, roles{}, themes{}, products{}, [principles])
ACTS = [
    # 1. Identify the Programme
    ("IP", "Sponsor the programme mandate",
     {"Sponsoring Group": "C", "Senior Responsible Owner": "C", "Programme Manager": "P"},
     {"Justification": "C", "Decisions": "P"},
     {"Business Case": "CR", "Vision Statement": "RF"}, ["Lead with purpose"]),
    ("IP", "Appoint the SRO and initial leadership",
     {"Sponsoring Group": "C", "Senior Responsible Owner": "P"},
     {"Organization": "C", "Structure": "P"},
     {"Organisation Structure & RACI": "CR"}, ["Deploy diverse skills"]),
    ("IP", "Develop the programme brief and outline vision",
     {"Senior Responsible Owner": "C", "Programme Manager": "P", "Business Change Manager": "P"},
     {"Design": "C", "Justification": "P"},
     {"Vision Statement": "CR", "Target Operating Model": "RF", "Business Case": "RF"},
     ["Lead with purpose"]),
    ("IP", "Confirm justification to proceed",
     {"Sponsoring Group": "C", "Senior Responsible Owner": "P"},
     {"Justification": "C", "Decisions": "C"},
     {"Business Case": "RV", "Programme Board Decision Log": "CR"}, ["Align with priorities"]),

    # 2. Design the Outcomes
    ("DO", "Define the target operating model",
     {"Programme Manager": "C", "Business Change Manager": "P", "Senior Responsible Owner": "P"},
     {"Design": "C", "Structure": "P"},
     {"Target Operating Model": "CR"}, []),
    ("DO", "Define benefits and benefit profiles",
     {"Business Change Manager": "C", "Programme Manager": "P"},
     {"Justification": "C", "Design": "P"},
     {"Benefit Profile(s)": "CR", "Benefits Realisation Plan": "RF"},
     ["Realize measurable benefits"]),
    ("DO", "Develop the full business case",
     {"Programme Manager": "C", "Senior Responsible Owner": "P"},
     {"Justification": "C"},
     {"Business Case": "RF"}, []),
    ("DO", "Confirm the programme organization and governance",
     {"Senior Responsible Owner": "C", "Programme Manager": "P", "Programme Office": "P"},
     {"Organization": "C", "Structure": "C", "Decisions": "P"},
     {"Organisation Structure & RACI": "RF"}, ["Deploy diverse skills"]),

    # 3. Plan Progressive Delivery
    ("PP", "Develop the programme plan",
     {"Programme Manager": "C", "Programme Office": "P"},
     {"Structure": "C", "Design": "P"},
     {"Programme Plan": "CR"}, []),
    ("PP", "Define tranches and the delivery approach",
     {"Programme Manager": "C", "Business Change Manager": "P"},
     {"Structure": "C", "Design": "P"},
     {"Tranche / Stage Plan": "CR", "Programme Plan": "RF"}, ["Bring pace and value"]),
    ("PP", "Establish the management approaches",
     {"Programme Office": "C", "Programme Manager": "P"},
     {"Knowledge": "C", "Assurance": "C"},
     {"Information Mgmt Approach": "CR", "Quality & Assurance Approach": "CR"},
     ["Deploy diverse skills"]),
    ("PP", "Set up risk and issue management",
     {"Programme Manager": "C", "Programme Office": "P"},
     {"Assurance": "C", "Decisions": "P"},
     {"Risk & Issue Register": "CR"}, []),

    # 4. Deliver the Capabilities
    ("DC", "Commission and coordinate the projects",
     {"Programme Manager": "C", "Programme Office": "P"},
     {"Structure": "C", "Knowledge": "P"},
     {"Tranche / Stage Plan": "UP", "Programme Plan": "UP"},
     ["Collaborate across boundaries"]),
    ("DC", "Manage tranche delivery",
     {"Programme Manager": "C", "Business Change Manager": "P"},
     {"Structure": "C", "Decisions": "P"},
     {"Programme Plan": "UP", "Risk & Issue Register": "UP"}, ["Bring pace and value"]),
    ("DC", "Assure delivery quality",
     {"Programme Office": "C", "Programme Manager": "P"},
     {"Assurance": "C"},
     {"Quality & Assurance Approach": "IM", "Audit / Assurance Log": "CR"}, []),
    ("DC", "Maintain stakeholder engagement and communications",
     {"Business Change Manager": "C", "Programme Manager": "P"},
     {"Knowledge": "C", "Organization": "P"},
     {"Information Mgmt Approach": "IM"}, ["Collaborate across boundaries"]),

    # 5. Embed the Outcomes
    ("EO", "Transition capability into operations",
     {"Business Change Manager": "C", "Programme Manager": "P"},
     {"Design": "C", "Structure": "P"},
     {"Target Operating Model": "IM"}, []),
    ("EO", "Realize and measure benefits",
     {"Business Change Manager": "C", "Senior Responsible Owner": "P"},
     {"Justification": "C"},
     {"Benefit Profile(s)": "RV", "Benefits Realisation Plan": "UP"},
     ["Realize measurable benefits"]),
    ("EO", "Confirm outcomes achieved",
     {"Senior Responsible Owner": "C", "Business Change Manager": "P"},
     {"Justification": "C", "Decisions": "P"},
     {"Business Case": "RV", "Programme Board Decision Log": "UP"}, []),

    # 6. Evaluate New Information
    ("EN", "Review programme progress and performance",
     {"Programme Manager": "C", "Senior Responsible Owner": "P", "Programme Office": "P"},
     {"Decisions": "C", "Assurance": "P"},
     {"Programme Plan": "RV", "Audit / Assurance Log": "UP"}, ["Deal with ambiguity"]),
    ("EN", "Assess risks, issues and change",
     {"Programme Manager": "C", "Programme Office": "P"},
     {"Decisions": "C", "Assurance": "P"},
     {"Risk & Issue Register": "UP"}, ["Deal with ambiguity"]),
    ("EN", "Re-confirm justification at tranche end",
     {"Senior Responsible Owner": "C", "Sponsoring Group": "P"},
     {"Justification": "C", "Decisions": "C"},
     {"Business Case": "RV", "Programme Board Decision Log": "UP"},
     ["Align with priorities"]),
    ("EN", "Capture and apply lessons",
     {"Programme Office": "C", "Programme Manager": "P"},
     {"Knowledge": "C"},
     {"Lessons Log": "UP"}, []),

    # 7. Close the Programme
    ("CP", "Confirm programme objectives are met",
     {"Senior Responsible Owner": "C", "Sponsoring Group": "P", "Business Change Manager": "P"},
     {"Justification": "C", "Decisions": "C"},
     {"Business Case": "RV", "Benefits Realisation Plan": "RV"}, ["Lead with purpose"]),
    ("CP", "Hand over ongoing benefits realization",
     {"Business Change Manager": "C", "Senior Responsible Owner": "P"},
     {"Justification": "C", "Design": "P"},
     {"Benefits Realisation Plan": "UP", "Target Operating Model": "RV"},
     ["Realize measurable benefits"]),
    ("CP", "Disband the programme organization",
     {"Senior Responsible Owner": "C", "Programme Office": "P"},
     {"Organization": "C", "Structure": "P"},
     {"Organisation Structure & RACI": "UP"}, []),
    ("CP", "Finalize lessons and assurance",
     {"Programme Office": "C", "Programme Manager": "P"},
     {"Knowledge": "C", "Assurance": "P"},
     {"Lessons Log": "UP", "Audit / Assurance Log": "RV"}, []),
]

PROC_NAME = {code: name for code, name, *_ in PROCESSES}


def build():
    entities = []
    relationships = []

    def ent(**kw):
        base = {"code": None, "subgroup": None, "parent": None, "confidence": "confirmed",
                "description": None, "sort_order": 0, "lifecycle_level": None,
                "lifecycle_phase": None, "sequence": None, "repeats": False}
        base.update(kw)
        entities.append(base)

    # processes
    for i, (code, name, lane, phase, seq, repeats, obj) in enumerate(PROCESSES, 1):
        ent(type="process", name=name, code=code, confidence="confirmed", description=obj,
            sort_order=i, lifecycle_level=lane, lifecycle_phase=phase, sequence=seq, repeats=repeats)
    # roles / themes / principles (confirmed vocabulary)
    for i, r in enumerate(ROLES, 1):
        ent(type="role", name=r, sort_order=i)
    for i, t in enumerate(THEMES, 1):
        ent(type="theme", name=t, sort_order=i)
    for i, p in enumerate(PRINCIPLES, 1):
        ent(type="principle", name=p, sort_order=i)
    for i, (prod, conf) in enumerate(PRODUCTS.items(), 1):
        ent(type="product", name=prod, confidence=conf, sort_order=i)

    # activities + relationships (indicative)
    order_by_proc = {}
    for (pcode, aname, roles, themes, products, principles) in ACTS:
        pname = PROC_NAME[pcode]
        order_by_proc[pcode] = order_by_proc.get(pcode, 0) + 1
        ent(type="activity", name=aname, parent=f"process::{pname}",
            confidence="indicative", sort_order=order_by_proc[pcode])
        src = f"activity::{aname}"
        for role, c in roles.items():
            relationships.append({"from": src, "to": f"role::{role}", "code": c, "confidence": "indicative"})
        for theme, c in themes.items():
            relationships.append({"from": src, "to": f"theme::{theme}", "code": c, "confidence": "indicative"})
        for prod, c in products.items():
            relationships.append({"from": src, "to": f"product::{prod}", "code": c, "confidence": "indicative"})
        for pr in principles:
            relationships.append({"from": src, "to": f"principle::{pr}", "code": "E", "confidence": "indicative"})

    doc = {
        "framework": {
            "key": "msp-5",
            "name": "MSP",
            "edition": "5th edition (Managing Successful Programmes, 2020)",
            "description": (
                "MSP 5th-edition Method Map: the 7 programme processes and their activities "
                "cross-referenced to roles, themes, products and the 7 principles. Role/theme "
                "codes: C=Responsible, P=Related, N=Assists. Product codes: CO=Confirmed, "
                "CR=Created, RF=Refined, RV=Reviewed, UP=Updated, IM=Implemented. The activity "
                "breakdown and every cross-reference mark are an indicative, best-effort "
                "reconstruction and must be SME-verified against the licensed MSP manual before "
                "formal use."
            ),
            "sort_order": 2,
            "config": CONFIG,
        },
        "entities": entities,
        "relationships": relationships,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"Wrote {os.path.abspath(OUT)}")
    print(f"  entities: {len(entities)}  relationships: {len(relationships)}")
    from collections import Counter
    print("  by type:", dict(Counter(e['type'] for e in entities)))


if __name__ == "__main__":
    build()
