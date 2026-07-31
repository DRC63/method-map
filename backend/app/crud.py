from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


# ---------- Framework ----------
def list_frameworks(db: Session) -> list[models.Framework]:
    return (
        db.query(models.Framework)
        .order_by(models.Framework.sort_order, models.Framework.name)
        .all()
    )


def get_framework(db: Session, framework_id: int) -> models.Framework | None:
    return db.get(models.Framework, framework_id)


def get_framework_by_key(db: Session, key: str) -> models.Framework | None:
    return db.query(models.Framework).filter(models.Framework.key == key).first()


def entity_counts(db: Session, framework_id: int) -> dict[str, int]:
    rows = (
        db.query(models.Entity.type, func.count(models.Entity.id))
        .filter(models.Entity.framework_id == framework_id)
        .group_by(models.Entity.type)
        .all()
    )
    return {t: c for t, c in rows}


# ---------- Entity ----------
def list_entities(
    db: Session,
    framework_id: int,
    type: str | None = None,
    search: str | None = None,
) -> list[models.Entity]:
    q = db.query(models.Entity).filter(models.Entity.framework_id == framework_id)
    if type:
        q = q.filter(models.Entity.type == type)
    if search:
        q = q.filter(models.Entity.name.ilike(f"%{search}%"))
    return q.order_by(models.Entity.type, models.Entity.sort_order, models.Entity.name).all()


def get_entity(db: Session, entity_id: int) -> models.Entity | None:
    return db.get(models.Entity, entity_id)


def create_entity(db: Session, data: schemas.EntityCreate) -> models.Entity:
    obj = models.Entity(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_entity(
    db: Session, obj: models.Entity, data: schemas.EntityUpdate
) -> models.Entity:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_entity(db: Session, obj: models.Entity) -> None:
    # Remove any relationships touching this entity first (SQLite FK-safe).
    db.query(models.Relationship).filter(
        (models.Relationship.from_entity_id == obj.id)
        | (models.Relationship.to_entity_id == obj.id)
    ).delete(synchronize_session=False)
    db.delete(obj)
    db.commit()


# ---------- Relationship ----------
def list_relationships(
    db: Session, framework_id: int
) -> list[models.Relationship]:
    return (
        db.query(models.Relationship)
        .filter(models.Relationship.framework_id == framework_id)
        .all()
    )


def relationships_for_entity(
    db: Session, entity_id: int
) -> list[models.Relationship]:
    return (
        db.query(models.Relationship)
        .filter(
            (models.Relationship.from_entity_id == entity_id)
            | (models.Relationship.to_entity_id == entity_id)
        )
        .all()
    )


def get_relationship(db: Session, rel_id: int) -> models.Relationship | None:
    return db.get(models.Relationship, rel_id)


def create_relationship(
    db: Session, data: schemas.RelationshipCreate
) -> models.Relationship:
    obj = models.Relationship(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_relationship(
    db: Session, obj: models.Relationship, data: schemas.RelationshipUpdate
) -> models.Relationship:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_relationship(db: Session, obj: models.Relationship) -> None:
    db.delete(obj)
    db.commit()
