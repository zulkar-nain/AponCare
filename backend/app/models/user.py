from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenants.tenant_id", index=True)
    email: str = Field(max_length=320, index=True)
    full_name: str = Field(max_length=200)
    password_hash: str
    role: str = Field(sa_column=Column(String(32), nullable=False))
    totp_secret: str | None = Field(default=None, max_length=64)
    totp_enabled: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default="false")
    )
    password_change_required: bool = Field(
        default=False, sa_column=Column(Boolean, nullable=False, server_default="false")
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
