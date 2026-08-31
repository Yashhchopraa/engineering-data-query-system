from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Geometry(BaseModel):
    geometry_type: str

    x: float
    y: float

    width: float
    height: float

    rotation: float

    x1: float
    y1: float
    x2: float
    y2: float


class ComponentConnection(BaseModel):
    source_uid: str
    target_uid: str
    connection_type: str


class DataQuality(BaseModel):
    flags: list[str] = Field(default_factory=list)

    duplicate_attributes_resolved: bool = False

    unknown_attributes: list[str] = Field(
        default_factory=list
    )


class EngineeringComponent(BaseModel):
    """
    Canonical representation of an engineering component.

    This object is intentionally independent of SQLite,
    Pandas, FastAPI, or the frontend.
    """

    component_id: str

    project_id: str | None = None

    component_type: str

    discipline: str

    zone: str

    geometry: Geometry

    attributes: dict[str, Any] = Field(
        default_factory=dict
    )

    connections: list[ComponentConnection] = Field(
        default_factory=list
    )

    unknown_attributes: dict[str, Any] = Field(
        default_factory=dict
    )

    data_quality: DataQuality = Field(
        default_factory=DataQuality
    )

    source_system: str = "synthetic_sqlite"

    source_schema: str = "engineering_model_v4"

    source_table: str = "spatial_entities"

    pipeline_run_id: str | None = None

    last_updated: str | None = None
