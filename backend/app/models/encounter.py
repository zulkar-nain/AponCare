from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class Encounter(SQLModel, table=True):
    __tablename__ = "encounters"

    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenants.tenant_id", index=True)
    patient_id: UUID = Field(foreign_key="patients.id")
    clinician_id: UUID | None = Field(default=None, foreign_key="users.id")
    summary: str
    occurred_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
