from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, String, func
from sqlmodel import Field, SQLModel


class Patient(SQLModel, table=True):
    __tablename__ = "patients"

    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenants.tenant_id", index=True)
    user_id: UUID | None = Field(default=None, foreign_key="users.id")
    full_name: str = Field(max_length=200)
    date_of_birth: date | None = None
    sex: str | None = Field(default=None, sa_column=Column(String(32), nullable=True))
    phone: str | None = Field(default=None, max_length=64)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
