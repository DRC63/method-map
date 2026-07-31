from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base
from .enums import Confidence


class Framework(Base):
    __tablename__ = "frameworks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    edition: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="framework", cascade="all, delete-orphan"
    )


class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = (
        UniqueConstraint("framework_id", "type", "name", name="uq_entity_identity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework_id: Mapped[int] = mapped_column(
        ForeignKey("frameworks.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, nullable=True)
    subgroup: Mapped[str | None] = mapped_column(String, nullable=True)
    # activity -> its owning process; null for everything else
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("entities.id"), nullable=True
    )
    confidence: Mapped[str] = mapped_column(
        String, default=Confidence.CONFIRMED.value
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Lifecycle / timeline metadata (mainly for processes): which swimlane the
    # process sits in, which phase of the project it runs in, its left-to-right
    # sequence, and whether it repeats each delivery stage. Null for entities
    # that have no place on the timeline.
    lifecycle_level: Mapped[str | None] = mapped_column(String, nullable=True)
    lifecycle_phase: Mapped[str | None] = mapped_column(String, nullable=True)
    sequence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    repeats: Mapped[bool] = mapped_column(Boolean, default=False)

    framework: Mapped["Framework"] = relationship(
        "Framework", back_populates="entities"
    )
    parent: Mapped["Entity"] = relationship("Entity", remote_side=[id])


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint(
            "from_entity_id", "to_entity_id", "code", name="uq_relationship"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework_id: Mapped[int] = mapped_column(
        ForeignKey("frameworks.id"), nullable=False
    )
    from_entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"), nullable=False
    )
    to_entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[str] = mapped_column(
        String, default=Confidence.INDICATIVE.value
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    from_entity: Mapped["Entity"] = relationship(
        "Entity", foreign_keys=[from_entity_id]
    )
    to_entity: Mapped["Entity"] = relationship("Entity", foreign_keys=[to_entity_id])
