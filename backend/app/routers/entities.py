from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, serializers
from ..database import get_db
from ..security import require_admin

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("/{entity_id}", response_model=schemas.EntityDetailOut)
def get_entity_detail(entity_id: int, db: Session = Depends(get_db)):
    obj = crud.get_entity(db, entity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Entity not found")
    return serializers.serialize_entity_detail(db, obj)


@router.post(
    "", response_model=schemas.EntityOut, status_code=201,
    dependencies=[Depends(require_admin)],
)
def create_entity(data: schemas.EntityCreate, db: Session = Depends(get_db)):
    if not crud.get_framework(db, data.framework_id):
        raise HTTPException(status_code=404, detail="Framework not found")
    return serializers.serialize_entity(crud.create_entity(db, data))


@router.put(
    "/{entity_id}", response_model=schemas.EntityOut,
    dependencies=[Depends(require_admin)],
)
def update_entity(
    entity_id: int, data: schemas.EntityUpdate, db: Session = Depends(get_db)
):
    obj = crud.get_entity(db, entity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Entity not found")
    return serializers.serialize_entity(crud.update_entity(db, obj, data))


@router.delete(
    "/{entity_id}", status_code=204, dependencies=[Depends(require_admin)]
)
def delete_entity(entity_id: int, db: Session = Depends(get_db)):
    obj = crud.get_entity(db, entity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Entity not found")
    crud.delete_entity(db, obj)
