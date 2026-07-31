"""Seed the database from the bundled JSON framework files in seed_data/.

Each file describes one framework: its entities (referenced by a composite
"type::name" key) and the relationships between them. Kept as data files rather
than inline code so an SME can regenerate/extend them (and so a future MSP file
drops in with zero code changes).

Run directly:  python -m app.seed [--force]
`--force` wipes and reseeds; otherwise a framework that already exists is skipped.
"""
import json
import os
import sys

from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from . import models

SEED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_data")


def _load_files() -> list[dict]:
    if not os.path.isdir(SEED_DIR):
        return []
    out = []
    for fname in sorted(os.listdir(SEED_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(SEED_DIR, fname), encoding="utf-8") as f:
                out.append(json.load(f))
    return out


def seed_framework(db: Session, data: dict) -> models.Framework:
    fw_data = data["framework"]
    framework = models.Framework(
        key=fw_data["key"],
        name=fw_data["name"],
        edition=fw_data.get("edition"),
        description=fw_data.get("description"),
        sort_order=fw_data.get("sort_order", 0),
    )
    db.add(framework)
    db.flush()  # assign framework.id

    # Pass 1: create every entity, remember it by its "type::name" key.
    key_to_entity: dict[str, models.Entity] = {}
    for e in data["entities"]:
        entity = models.Entity(
            framework_id=framework.id,
            type=e["type"],
            name=e["name"],
            code=e.get("code"),
            subgroup=e.get("subgroup"),
            confidence=e.get("confidence", "confirmed"),
            description=e.get("description"),
            sort_order=e.get("sort_order", 0),
            lifecycle_level=e.get("lifecycle_level"),
            lifecycle_phase=e.get("lifecycle_phase"),
            sequence=e.get("sequence"),
            repeats=e.get("repeats", False),
        )
        db.add(entity)
        key_to_entity[f'{e["type"]}::{e["name"]}'] = entity
    db.flush()  # assign entity ids

    # Pass 2: wire up parents (activity -> process).
    for e in data["entities"]:
        parent_key = e.get("parent")
        if parent_key and parent_key in key_to_entity:
            child = key_to_entity[f'{e["type"]}::{e["name"]}']
            child.parent_id = key_to_entity[parent_key].id

    # Pass 3: relationships.
    for r in data.get("relationships", []):
        src = key_to_entity.get(r["from"])
        tgt = key_to_entity.get(r["to"])
        if not src or not tgt:
            continue
        db.add(
            models.Relationship(
                framework_id=framework.id,
                from_entity_id=src.id,
                to_entity_id=tgt.id,
                code=r["code"],
                confidence=r.get("confidence", "indicative"),
                note=r.get("note"),
            )
        )
    db.commit()
    return framework


def seed(db: Session, force: bool = False) -> None:
    files = _load_files()
    for data in files:
        key = data["framework"]["key"]
        existing = (
            db.query(models.Framework).filter(models.Framework.key == key).first()
        )
        if existing:
            if not force:
                continue
            db.delete(existing)  # cascades to entities; relationships cleared below
            db.query(models.Relationship).filter(
                models.Relationship.framework_id == existing.id
            ).delete(synchronize_session=False)
            db.commit()
        seed_framework(db, data)


def main() -> None:
    force = "--force" in sys.argv
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db, force=force)
        fw_count = db.query(models.Framework).count()
        ent_count = db.query(models.Entity).count()
        rel_count = db.query(models.Relationship).count()
    print(
        f"Seed complete (force={force}): {fw_count} framework(s), "
        f"{ent_count} entities, {rel_count} relationships."
    )


if __name__ == "__main__":
    main()
