"""ORM -> Pydantic conversion, including enriched fields (parent names, code
labels, relationship direction) that aren't plain columns.
"""
from . import crud, models, schemas
from .graph import _framework_meta


def serialize_framework(
    framework: models.Framework, counts: dict[str, int] | None = None
) -> schemas.FrameworkOut:
    return schemas.FrameworkOut(
        id=framework.id,
        key=framework.key,
        name=framework.name,
        edition=framework.edition,
        description=framework.description,
        sort_order=framework.sort_order,
        entity_counts=counts or {},
        config=framework.config or {},
    )


def serialize_entity(entity: models.Entity) -> schemas.EntityOut:
    return schemas.EntityOut(
        id=entity.id,
        framework_id=entity.framework_id,
        type=entity.type,
        name=entity.name,
        code=entity.code,
        subgroup=entity.subgroup,
        parent_id=entity.parent_id,
        confidence=entity.confidence,
        description=entity.description,
        sort_order=entity.sort_order,
        lifecycle_level=entity.lifecycle_level,
        lifecycle_phase=entity.lifecycle_phase,
        sequence=entity.sequence,
        repeats=entity.repeats,
        parent_name=entity.parent.name if entity.parent else None,
    )


def serialize_entity_detail(
    db, entity: models.Entity
) -> schemas.EntityDetailOut:
    base = serialize_entity(entity)
    related: list[schemas.RelatedEntityOut] = []
    framework = crud.get_framework(db, entity.framework_id)
    container_type, hub_type, code_labels = _framework_meta(framework)

    # A container (process) has no relationships of its own — it *contains* hubs
    # (activities). Surface those in sequence so it isn't a dead end in the graph.
    if entity.type == container_type:
        children = sorted(
            (
                e
                for e in crud.list_entities(db, entity.framework_id, type=hub_type)
                if e.parent_id == entity.id
            ),
            key=lambda a: a.sort_order,
        )
        for i, child in enumerate(children, start=1):
            related.append(
                schemas.RelatedEntityOut(
                    relationship_id=-child.id,
                    entity_id=child.id,
                    type=hub_type,
                    name=child.name,
                    code=str(i),
                    code_label=f"step {i}",
                    confidence=child.confidence,
                    direction="out",
                    via_process=None,
                )
            )
        return schemas.EntityDetailOut(**base.model_dump(), related=related)

    rels = crud.relationships_for_entity(db, entity.id)
    for rel in rels:
        if rel.from_entity_id == entity.id:
            other = rel.to_entity
            direction = "out"
            via_process = None
        else:
            other = rel.from_entity
            direction = "in"
            # incoming links come from activities; surface the owning process
            via_process = (
                other.parent.name if other and other.parent else None
            )
        if other is None:
            continue
        related.append(
            schemas.RelatedEntityOut(
                relationship_id=rel.id,
                entity_id=other.id,
                type=other.type,
                name=other.name,
                code=rel.code,
                code_label=code_labels.get(rel.code, rel.code),
                confidence=rel.confidence,
                direction=direction,
                via_process=via_process,
            )
        )
    # order: outgoing first, then by type, then name
    related.sort(key=lambda r: (r.direction != "out", r.type, r.name))
    return schemas.EntityDetailOut(**base.model_dump(), related=related)


def serialize_relationship(rel: models.Relationship) -> schemas.RelationshipOut:
    return schemas.RelationshipOut(
        id=rel.id,
        framework_id=rel.framework_id,
        from_entity_id=rel.from_entity_id,
        to_entity_id=rel.to_entity_id,
        code=rel.code,
        confidence=rel.confidence,
        note=rel.note,
        from_name=rel.from_entity.name if rel.from_entity else None,
        to_name=rel.to_entity.name if rel.to_entity else None,
        from_type=rel.from_entity.type if rel.from_entity else None,
        to_type=rel.to_entity.type if rel.to_entity else None,
    )
