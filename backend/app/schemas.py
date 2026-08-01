from pydantic import BaseModel, ConfigDict, Field


# ---------- Framework ----------
class FrameworkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    key: str
    name: str
    edition: str | None = None
    description: str | None = None
    sort_order: int = 0
    entity_counts: dict[str, int] = {}
    config: dict = {}


# ---------- Entity ----------
class EntityBase(BaseModel):
    type: str
    name: str
    code: str | None = None
    subgroup: str | None = None
    parent_id: int | None = None
    confidence: str = "confirmed"
    description: str | None = None
    sort_order: int = 0
    lifecycle_level: str | None = None
    lifecycle_phase: str | None = None
    sequence: int | None = None
    repeats: bool = False


class EntityCreate(EntityBase):
    framework_id: int


class EntityUpdate(BaseModel):
    type: str | None = None
    name: str | None = None
    code: str | None = None
    subgroup: str | None = None
    parent_id: int | None = None
    confidence: str | None = None
    description: str | None = None
    sort_order: int | None = None
    lifecycle_level: str | None = None
    lifecycle_phase: str | None = None
    sequence: int | None = None
    repeats: bool | None = None


class EntityOut(EntityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    framework_id: int
    parent_name: str | None = None


# A relationship as seen from one entity's point of view (for the detail panel).
class RelatedEntityOut(BaseModel):
    relationship_id: int
    entity_id: int
    type: str
    name: str
    code: str
    code_label: str
    confidence: str
    direction: str  # "out" (this entity is the source) or "in"
    via_process: str | None = None  # for incoming links, the activity's process


class EntityDetailOut(EntityOut):
    related: list[RelatedEntityOut] = []


# ---------- Relationship ----------
class RelationshipBase(BaseModel):
    from_entity_id: int
    to_entity_id: int
    code: str
    confidence: str = "indicative"
    note: str | None = None


class RelationshipCreate(RelationshipBase):
    framework_id: int


class RelationshipUpdate(BaseModel):
    code: str | None = None
    confidence: str | None = None
    note: str | None = None


class RelationshipOut(RelationshipBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    framework_id: int
    from_name: str | None = None
    to_name: str | None = None
    from_type: str | None = None
    to_type: str | None = None


# ---------- Graph ----------
class GraphNode(BaseModel):
    id: int
    type: str
    name: str
    code: str | None = None
    subgroup: str | None = None
    confidence: str = "confirmed"
    degree: int = 0
    direct_degree: int = 0
    parent_id: int | None = None
    sort_order: int = 0
    sequence: int | None = None
    lifecycle_level: str | None = None
    lifecycle_phase: str | None = None


class GraphLink(BaseModel):
    source: int
    target: int
    kind: str  # "direct" | "contains" | "derived"
    code: str | None = None
    code_label: str | None = None
    confidence: str | None = None
    weight: int = 1


class GraphOut(BaseModel):
    framework: FrameworkOut
    nodes: list[GraphNode] = Field(default_factory=list)
    links: list[GraphLink] = Field(default_factory=list)


# ---------- Lifecycle (process model / timeline) ----------
class LifecycleActivity(BaseModel):
    id: int
    name: str
    sequence: int


class LifecycleProcess(BaseModel):
    id: int
    code: str | None = None
    name: str
    description: str | None = None
    lifecycle_level: str | None = None
    lifecycle_phase: str | None = None
    sequence: int | None = None
    repeats: bool = False
    activities: list[LifecycleActivity] = Field(default_factory=list)


class LifecycleOut(BaseModel):
    framework: FrameworkOut
    levels: dict[str, str] = Field(default_factory=dict)
    level_order: list[str] = Field(default_factory=list)
    phases: dict[str, str] = Field(default_factory=dict)
    phase_order: list[str] = Field(default_factory=list)
    processes: list[LifecycleProcess] = Field(default_factory=list)
