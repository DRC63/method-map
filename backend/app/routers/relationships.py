from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, serializers
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/api/relationships", tags=["relationships"])


def _validate_endpoints(db: Session, framework_id: int, from_id: int, to_id: int):
    src = crud.get_entity(db, from_id)
    tgt = crud.get_entity(db, to_id)
    if not src or not tgt:
        raise HTTPException(status_code=404, detail="Entity not found")
    if src.framework_id != framework_id or tgt.framework_id != framework_id:
        raise HTTPException(
            status_code=400, detail="Entities must belong to the framework"
        )


@router.post(
    "", response_model=schemas.RelationshipOut, status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_relationship(data: schemas.RelationshipCreate, db: Session = Depends(get_db)):
    if not crud.get_framework(db, data.framework_id):
        raise HTTPException(status_code=404, detail="Framework not found")
    _validate_endpoints(db, data.framework_id, data.from_entity_id, data.to_entity_id)
    return serializers.serialize_relationship(crud.create_relationship(db, data))


@router.put(
    "/{rel_id}", response_model=schemas.RelationshipOut,
    dependencies=[Depends(require_admin)],
)
def update_relationship(
    rel_id: int, data: schemas.RelationshipUpdate, db: Session = Depends(get_db)
):
    obj = crud.get_relationship(db, rel_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return serializers.serialize_relationship(crud.update_relationship(db, obj, data))


@router.delete(
    "/{rel_id}", status_code=204, dependencies=[Depends(require_admin)]
)
def delete_relationship(rel_id: int, db: Session = Depends(get_db)):
    obj = crud.get_relationship(db, rel_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Relationship not found")
    crud.delete_relationship(db, obj)
