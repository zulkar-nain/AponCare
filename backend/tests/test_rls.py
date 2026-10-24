import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="Set TEST_DATABASE_URL to a dedicated database migrated with Alembic",
)


@pytest.mark.asyncio
async def test_tenant_cannot_read_other_tenant_patients() -> None:
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    tenant_a, tenant_b = uuid4(), uuid4()
    patient_a, patient_b = uuid4(), uuid4()

    try:
        async with sessions() as session:
            async with session.begin():
                is_superuser = await session.scalar(
                    text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")
                )
                assert is_superuser is False, (
                    "TEST_DATABASE_URL must use a non-superuser role or PostgreSQL bypasses RLS"
                )
                await session.execute(
                    text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
                    {"tenant_id": str(tenant_a)},
                )
                await session.execute(
                    text("INSERT INTO tenants (tenant_id, name) VALUES (:id, 'Tenant A')"),
                    {"id": tenant_a},
                )
                await session.execute(
                    text("""
                        INSERT INTO patients (id, tenant_id, full_name)
                        VALUES (:patient_id, :tenant_id, 'Patient A')
                    """),
                    {"patient_id": patient_a, "tenant_id": tenant_a},
                )
                await session.execute(
                    text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
                    {"tenant_id": str(tenant_b)},
                )
                await session.execute(
                    text("INSERT INTO tenants (tenant_id, name) VALUES (:id, 'Tenant B')"),
                    {"id": tenant_b},
                )
                await session.execute(
                    text("""
                        INSERT INTO patients (id, tenant_id, full_name)
                        VALUES (:patient_id, :tenant_id, 'Patient B')
                    """),
                    {"patient_id": patient_b, "tenant_id": tenant_b},
                )
                await session.execute(
                    text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
                    {"tenant_id": str(tenant_a)},
                )
                result = await session.execute(
                    text("SELECT id FROM patients WHERE id = :patient_id"),
                    {"patient_id": patient_b},
                )
                assert result.scalar_one_or_none() is None

                visible = await session.execute(text("SELECT id FROM patients"))
                assert {row.id for row in visible} == {patient_a}
    finally:
        async with sessions() as session:
            async with session.begin():
                for tenant_id in (tenant_a, tenant_b):
                    await session.execute(
                        text("SELECT set_config('app.current_tenant', :tenant_id, true)"),
                        {"tenant_id": str(tenant_id)},
                    )
                    await session.execute(
                        text("DELETE FROM tenants WHERE tenant_id = :tenant_id"),
                        {"tenant_id": tenant_id},
                    )
        await engine.dispose()
