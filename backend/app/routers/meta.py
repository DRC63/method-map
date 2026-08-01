import os

from fastapi import APIRouter
from pydantic import BaseModel

from ..enums import (
    CODE_LABELS,
    ENTITY_TYPE_ORDER,
    PRODUCT_CODES,
    PRODUCT_SUBGROUPS,
    ROLE_CODES,
)
from ..security import check_password

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/meta")
def get_meta():
    """Static reference data the frontend uses to build legends and forms."""
    return {
        "entity_types": ENTITY_TYPE_ORDER,
        "code_labels": CODE_LABELS,
        "role_codes": ROLE_CODES,
        "product_codes": PRODUCT_CODES,
        "product_subgroups": PRODUCT_SUBGROUPS,
        # Which framework a single-framework deployment should default to
        # (null = show the first / let the client choose).
        "default_framework": os.getenv("FRAMEWORK_KEY"),
    }


class PasswordIn(BaseModel):
    password: str


@router.post("/auth/verify")
def verify_password(data: PasswordIn):
    """Lets the frontend unlock authoring mode. Returns 200/{ok:true} on match."""
    return {"ok": check_password(data.password)}
