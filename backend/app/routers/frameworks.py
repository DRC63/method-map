from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from .. import crud, exports, graph, schemas, serializers
from ..database import get_db
from ..enums import (
    LIFECYCLE_LEVEL_ORDER,
    LIFECYCLE_LEVELS,
    LIFECYCLE_PHASE_ORDER,
    LIFECYCLE_PHASES,
    EntityType,
)

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


def _framework_or_404(db: Session, key: str):
    fw = crud.get_framework_by_key(db, key)
    if not fw:
        raise HTTPException(status_code=404, detail="Framework not found")
    return fw


@router.get("", response_model=list[schemas.FrameworkOut])
def list_frameworks(db: Session = Depends(get_db)):
    out = []
    for fw in crud.list_frameworks(db):
        out.append(serializers.serialize_framework(fw, crud.entity_counts(db, fw.id)))
    return out


@router.get("/{key}", response_model=schemas.FrameworkOut)
def get_framework(key: str, db: Session = Depends(get_db)):
    fw = _framework_or_404(db, key)
    return serializers.serialize_framework(fw, crud.entity_counts(db, fw.id))


@router.get("/{key}/entities", response_model=list[schemas.EntityOut])
def list_entities(
    key: str,
    type: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    fw = _framework_or_404(db, key)
    return [
        serializers.serialize_entity(e)
        for e in crud.list_entities(db, fw.id, type=type, search=search)
    ]


@router.get("/{key}/relationships", response_model=list[schemas.RelationshipOut])
def list_relationships(key: str, db: Session = Depends(get_db)):
    fw = _framework_or_404(db, key)
    return [
        serializers.serialize_relationship(r)
        for r in crud.list_relationships(db, fw.id)
    ]


@router.get("/{key}/graph", response_model=schemas.GraphOut)
def get_graph(
    key: str,
    types: str = Query(
        default=",".join(t.value for t in EntityType),
        description="Comma-separated entity types to include as nodes.",
    ),
    derived: bool = Query(
        default=True,
        description="Include co-occurrence links between non-activity entities.",
    ),
    db: Session = Depends(get_db),
):
    fw = _framework_or_404(db, key)
    valid = {t.value for t in EntityType}
    selected = {t.strip() for t in types.split(",") if t.strip() in valid}
    if not selected:
        selected = valid
    result = graph.build_graph(db, fw, selected, include_derived=derived)
    return schemas.GraphOut(
        framework=serializers.serialize_framework(fw, crud.entity_counts(db, fw.id)),
        nodes=result["nodes"],
        links=result["links"],
    )


@router.get("/{key}/lifecycle", response_model=schemas.LifecycleOut)
def get_lifecycle(key: str, db: Session = Depends(get_db)):
    """Processes in timeline order, each with its activities in sequence — the
    data behind the Lifecycle (process-model) view."""
    fw = _framework_or_404(db, key)
    all_entities = crud.list_entities(db, fw.id)
    activities_by_process: dict[int, list] = {}
    for e in all_entities:
        if e.type == EntityType.ACTIVITY.value and e.parent_id is not None:
            activities_by_process.setdefault(e.parent_id, []).append(e)

    processes = [e for e in all_entities if e.type == EntityType.PROCESS.value]
    processes.sort(key=lambda p: (p.sequence if p.sequence is not None else p.sort_order))

    out_processes = []
    for p in processes:
        acts = sorted(
            activities_by_process.get(p.id, []), key=lambda a: a.sort_order
        )
        out_processes.append(
            schemas.LifecycleProcess(
                id=p.id,
                code=p.code,
                name=p.name,
                description=p.description,
                lifecycle_level=p.lifecycle_level,
                lifecycle_phase=p.lifecycle_phase,
                sequence=p.sequence,
                repeats=p.repeats,
                activities=[
                    schemas.LifecycleActivity(id=a.id, name=a.name, sequence=i + 1)
                    for i, a in enumerate(acts)
                ],
            )
        )
    return schemas.LifecycleOut(
        framework=serializers.serialize_framework(fw, crud.entity_counts(db, fw.id)),
        levels=LIFECYCLE_LEVELS,
        level_order=LIFECYCLE_LEVEL_ORDER,
        phases=LIFECYCLE_PHASES,
        phase_order=LIFECYCLE_PHASE_ORDER,
        processes=out_processes,
    )


# ---------- exports ----------
@router.get("/{key}/export.csv")
def export_csv(key: str, focus_entity_id: int | None = None, db: Session = Depends(get_db)):
    fw = _framework_or_404(db, key)
    data = exports.export_csv(db, fw, focus_entity_id)
    return Response(
        content=data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{key}-crossref.csv"'},
    )


@router.get("/{key}/export.xlsx")
def export_xlsx(key: str, focus_entity_id: int | None = None, db: Session = Depends(get_db)):
    fw = _framework_or_404(db, key)
    data = exports.export_xlsx(db, fw, focus_entity_id)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{key}-crossref.xlsx"'},
    )


@router.get("/{key}/entities/{entity_id}/report.pdf")
def entity_report(key: str, entity_id: int, db: Session = Depends(get_db)):
    fw = _framework_or_404(db, key)
    entity = crud.get_entity(db, entity_id)
    if not entity or entity.framework_id != fw.id:
        raise HTTPException(status_code=404, detail="Entity not found")
    data = exports.entity_report_pdf(db, fw, entity)
    safe = entity.name.replace(" ", "_").replace("/", "-")
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe}.pdf"'},
    )
