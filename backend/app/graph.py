"""Builds the node/link graph the frontend renders.

The data is hub-centric: every stored relationship goes from a **hub** entity (an
activity, in PRINCE2) to a **node** entity (role / practice / approach / product)
with a code, and each hub belongs to a **container** (a process). Which type plays
each role is declared in the framework's config (kind: container | hub | node), so
this logic is framework-agnostic. From that we produce three link kinds, depending
on which entity-type layers the user has switched on:

  - "contains" : container -> hub   (structural, when both layers visible)
  - "direct"   : hub -> node        (the stored code, when both layers visible)
  - "derived"  : X <-> Y            (two non-hub entities that co-occur on the same
                 hub; weight = how many hubs they share)

A container is treated as an implicit participant in each of its hubs, so
container<->node derived links appear too.
"""
from itertools import combinations

from sqlalchemy.orm import Session

from . import crud, models


def _framework_meta(framework: models.Framework):
    """(container_type, hub_type, code_labels) from the framework config."""
    cfg = framework.config or {}
    types = cfg.get("types", [])
    container = next((t["key"] for t in types if t.get("kind") == "container"), "process")
    hub = next((t["key"] for t in types if t.get("kind") == "hub"), "activity")
    code_labels: dict[str, str] = {}
    for group in (cfg.get("codes") or {}).values():
        code_labels.update(group)
    return container, hub, code_labels


def build_graph(
    db: Session,
    framework: models.Framework,
    types: set[str],
    include_derived: bool = True,
) -> dict:
    container_type, hub_type, code_labels = _framework_meta(framework)
    entities = {e.id: e for e in crud.list_entities(db, framework.id)}
    rels = crud.list_relationships(db, framework.id)

    visible_ids: set[int] = set()
    links: list[dict] = []
    degree: dict[int, int] = {}

    def bump(a: int, b: int):
        degree[a] = degree.get(a, 0) + 1
        degree[b] = degree.get(b, 0) + 1

    # "Direct degree" = number of actual coded relationships a node takes part in,
    # independent of the visible layers and the derived toggle — its real "direct
    # responsibilities" count, used for node-size weighting. Containers have no
    # relationships of their own, so we size them by how many hubs they contain.
    direct_deg: dict[int, int] = {}
    for rel in rels:
        direct_deg[rel.from_entity_id] = direct_deg.get(rel.from_entity_id, 0) + 1
        direct_deg[rel.to_entity_id] = direct_deg.get(rel.to_entity_id, 0) + 1
    child_counts: dict[int, int] = {}
    for e in entities.values():
        if e.type == hub_type and e.parent_id:
            child_counts[e.parent_id] = child_counts.get(e.parent_id, 0) + 1

    hub_visible = hub_type in types
    container_visible = container_type in types

    # ----- structural: container -> hub -----
    if hub_visible and container_visible:
        for e in entities.values():
            if e.type == hub_type and e.parent_id in entities:
                if entities[e.parent_id].type == container_type:
                    visible_ids.add(e.id)
                    visible_ids.add(e.parent_id)
                    links.append(
                        {"source": e.parent_id, "target": e.id, "kind": "contains", "weight": 1}
                    )
                    bump(e.parent_id, e.id)

    # ----- direct: hub -> node -----
    if hub_visible:
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
                        "code_label": code_labels.get(rel.code, rel.code),
                        "confidence": rel.confidence,
                        "weight": 1,
                    }
                )
                bump(src.id, tgt.id)

    # ----- derived: co-occurrence through shared hubs -----
    if include_derived:
        by_hub: dict[int, set[int]] = {}
        for rel in rels:
            hub = entities.get(rel.from_entity_id)
            tgt = entities.get(rel.to_entity_id)
            if not hub or not tgt:
                continue
            if tgt.type in types and tgt.type != hub_type:
                by_hub.setdefault(hub.id, set()).add(tgt.id)

        if container_visible:
            for hub_id, members in by_hub.items():
                hub = entities.get(hub_id)
                if hub and hub.parent_id in entities:
                    parent = entities[hub.parent_id]
                    if parent.type == container_type:
                        members.add(parent.id)

        pair_weight: dict[tuple[int, int], int] = {}
        for members in by_hub.values():
            for a, b in combinations(sorted(members), 2):
                pair_weight[(a, b)] = pair_weight.get((a, b), 0) + 1

        for (a, b), w in pair_weight.items():
            visible_ids.add(a)
            visible_ids.add(b)
            links.append({"source": a, "target": b, "kind": "derived", "weight": w})
            bump(a, b)

    # Include any visible-type entity even if it has no links, so isolated nodes
    # still show up (e.g. an SME-added node not yet wired to anything).
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
                    if e.type == container_type
                    else direct_deg.get(e.id, 0)
                ),
                "parent_id": e.parent_id,
                "sort_order": e.sort_order,
                "sequence": e.sequence,
                "lifecycle_level": e.lifecycle_level,
                "lifecycle_phase": e.lifecycle_phase,
            }
        )
    nodes.sort(key=lambda n: (n["type"], n["name"]))
    return {"nodes": nodes, "links": links}
