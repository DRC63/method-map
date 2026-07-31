"""Builds the node/link graph the frontend renders.

The underlying data is activity-centric: every stored relationship goes from an
activity to a role / practice / approach / product with a C/P/N/I/O/U/A code, and
each activity belongs to a process. From that we produce three kinds of link,
depending on which entity-type layers the user has switched on:

  - "contains" : process -> activity  (structural, when both layers visible)
  - "direct"   : activity -> target   (the stored code, when both layers visible)
  - "derived"  : X <-> Y              (two non-activity entities that co-occur on
                 the same activity; weight = how many activities they share)

Derived links are what let the user hide Activities and still see, say, how Roles
relate to Practices or Products - the connection runs *through* shared activities.
A process is treated as an implicit participant in each of its activities, so
process<->role / process<->product derived links appear too.
"""
from itertools import combinations

from sqlalchemy.orm import Session

from . import crud, models
from .enums import CODE_LABELS, EntityType


def build_graph(
    db: Session,
    framework: models.Framework,
    types: set[str],
    include_derived: bool = True,
) -> dict:
    entities = {e.id: e for e in crud.list_entities(db, framework.id)}
    rels = crud.list_relationships(db, framework.id)

    visible_ids: set[int] = set()
    links: list[dict] = []
    degree: dict[int, int] = {}

    def bump(a: int, b: int):
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1

    # "Direct degree" = number of actual coded relationships (C/P/N/I/O/U/A) a node
    # takes part in, independent of the visible layers and the derived-links toggle.
    # This is the node's real "direct responsibilities" count, used for weighting
    # node size. Processes have no relationships of their own, so we size them by
    # how many activities they contain instead.
    direct_deg: dict[int, int] = {}
    for rel in rels:
        direct_deg[rel.from_entity_id] = direct_deg.get(rel.from_entity_id, 0) + 1
        direct_deg[rel.to_entity_id] = direct_deg.get(rel.to_entity_id, 0) + 1
    child_counts: dict[int, int] = {}
    for e in entities.values():
        if e.type == EntityType.ACTIVITY.value and e.parent_id:
            child_counts[e.parent_id] = child_counts.get(e.parent_id, 0) + 1

    activity_visible = EntityType.ACTIVITY.value in types
    process_visible = EntityType.PROCESS.value in types

    # ----- structural: process -> activity -----
    if activity_visible and process_visible:
        for e in entities.values():
            if e.type == EntityType.ACTIVITY.value and e.parent_id in entities:
                if entities[e.parent_id].type == EntityType.PROCESS.value:
                    visible_ids.add(e.id)
                    visible_ids.add(e.parent_id)
                    links.append(
                        {
                            "source": e.parent_id,
                            "target": e.id,
                            "kind": "contains",
                            "weight": 1,
                        }
                    )
                    bump(e.parent_id, e.id)

    # ----- direct: activity -> target -----
    if activity_visible:
        for rel in rels:
            src = entities.get(rel.from_entity_id)
            tgt = entities.get(rel.to_entity_id)
            if not src or not tgt:
                continue
            if tgt.type in types:
                visible_ids.add(src.id)
                visible_ids.add(tgt.id)
                links.append(
                    {
                        "source": src.id,
                        "target": tgt.id,
                        "kind": "direct",
                        "code": rel.code,
                        "code_label": CODE_LABELS.get(rel.code, rel.code),
                        "confidence": rel.confidence,
                        "weight": 1,
                    }
                )
                bump(src.id, tgt.id)

    # ----- derived: co-occurrence through shared activities -----
    if include_derived:
        # For each activity, collect the set of visible non-activity participants
        # (its targets + its owning process), then link every pair of them.
        by_activity: dict[int, set[int]] = {}
        for rel in rels:
            act = entities.get(rel.from_entity_id)
            tgt = entities.get(rel.to_entity_id)
            if not act or not tgt:
                continue
            if tgt.type in types and tgt.type != EntityType.ACTIVITY.value:
                by_activity.setdefault(act.id, set()).add(tgt.id)

        if process_visible:
            for act_id, members in by_activity.items():
                act = entities.get(act_id)
                if act and act.parent_id in entities:
                    parent = entities[act.parent_id]
                    if parent.type == EntityType.PROCESS.value:
                        members.add(parent.id)

        pair_weight: dict[tuple[int, int], int] = {}
        for members in by_activity.values():
            for a, b in combinations(sorted(members), 2):
                pair_weight[(a, b)] = pair_weight.get((a, b), 0) + 1

        for (a, b), w in pair_weight.items():
            visible_ids.add(a)
            visible_ids.add(b)
            links.append(
                {
                    "source": a,
                    "target": b,
                    "kind": "derived",
                    "weight": w,
                }
            )
            bump(a, b)

    # Include any visible-type entity even if it has no links, so isolated
    # nodes still show up (e.g. an SME-added role not yet wired to anything).
    for e in entities.values():
        if e.type in types:
            visible_ids.add(e.id)

    nodes = []
    for eid in visible_ids:
        e = entities[eid]
        nodes.append(
            {
                "id": e.id,
                "type": e.type,
                "name": e.name,
                "code": e.code,
                "subgroup": e.subgroup,
                "confidence": e.confidence,
                "degree": degree.get(e.id, 0),
                "direct_degree": (
                    child_counts.get(e.id, 0)
                    if e.type == EntityType.PROCESS.value
                    else direct_deg.get(e.id, 0)
                ),
                "parent_id": e.parent_id,
                "sort_order": e.sort_order,
            }
        )
    nodes.sort(key=lambda n: (n["type"], n["name"]))
    return {"nodes": nodes, "links": links}
