import enum


class EntityType(str, enum.Enum):
    PROCESS = "process"
    ACTIVITY = "activity"
    ROLE = "role"
    PRACTICE = "practice"
    APPROACH = "approach"
    PRODUCT = "product"


# The order entity types are stacked/coloured in the UI legend.
ENTITY_TYPE_ORDER = [t.value for t in EntityType]


class Confidence(str, enum.Enum):
    CONFIRMED = "confirmed"
    INDICATIVE = "indicative"


# Relationship codes and their human labels.
# C/P/N apply to roles, practices and management approaches.
# I/O/U/A apply to products.
ROLE_CODES = {
    "C": "Responsible",
    "P": "Participates",
    "N": "Assists",
}
PRODUCT_CODES = {
    "I": "Input",
    "O": "Output",
    "U": "Update",
    "A": "Authorise",
}
CODE_LABELS = {**ROLE_CODES, **PRODUCT_CODES}

PRODUCT_SUBGROUPS = {
    "baseline": "Baselines",
    "log": "Project Log",
    "report": "Reports",
}

# Lifecycle swimlanes (who is accountable) and the project phases time flows
# through. Used by the Lifecycle / process-model view.
LIFECYCLE_LEVELS = {
    "directing": "Directing (Project Board)",
    "managing": "Managing (Project Manager)",
    "delivering": "Delivering (Team)",
}
LIFECYCLE_LEVEL_ORDER = ["directing", "managing", "delivering"]

LIFECYCLE_PHASES = {
    "pre-project": "Pre-project",
    "initiation": "Initiation stage",
    "delivery": "Delivery stage(s)",
    "stage-boundary": "Stage boundary",
    "final": "Final delivery stage",
    "throughout": "Throughout",
}
LIFECYCLE_PHASE_ORDER = [
    "pre-project",
    "initiation",
    "delivery",
    "stage-boundary",
    "final",
    "throughout",
]
