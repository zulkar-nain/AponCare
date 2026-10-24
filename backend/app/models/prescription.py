from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Column, DateTime, JSON, func
from sqlmodel import Field, SQLModel


class Prescription(SQLModel, table=True):
    __tablename__ = "prescriptions"

    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenants.tenant_id", index=True)
    patient_id: UUID = Field(foreign_key="patients.id")
    encounter_id: UUID | None = Field(default=None, foreign_key="encounters.id")
    authored_by: UUID | None = Field(default=None, foreign_key="users.id")
    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
