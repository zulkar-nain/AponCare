"""Create tenant-aware HMIS tables and enforce tenant RLS."""

import os
import re

from alembic import op

revision = "0001_initial_rls"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    statements = [
        """
        CREATE TABLE tenants (
            tenant_id uuid PRIMARY KEY,
            name varchar(200) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """,
        """
        CREATE TABLE users (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            email varchar(320) NOT NULL,
            full_name varchar(200) NOT NULL,
            password_hash text NOT NULL,
            role varchar(32) NOT NULL CHECK (role IN
                ('super_admin', 'org_admin', 'staff', 'medical_team', 'patient_portal')),
            totp_secret varchar(64),
            totp_enabled boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, email),
            UNIQUE (tenant_id, id)
        )
        """,
        """
        CREATE TABLE patients (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            user_id uuid,
            full_name varchar(200) NOT NULL,
            date_of_birth date,
            sex varchar(32),
            phone varchar(64),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, user_id) REFERENCES users(tenant_id, id)
                ON DELETE SET NULL (user_id)
        )
        """,
        """
        CREATE TABLE encounters (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            patient_id uuid NOT NULL,
            clinician_id uuid,
            summary text NOT NULL,
            occurred_at timestamptz NOT NULL DEFAULT now(),
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, id),
            FOREIGN KEY (tenant_id, patient_id) REFERENCES patients(tenant_id, id)
                ON DELETE CASCADE,
            FOREIGN KEY (tenant_id, clinician_id) REFERENCES users(tenant_id, id)
                ON DELETE SET NULL (clinician_id)
        )
        """,
        """
        CREATE TABLE prescriptions (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
            patient_id uuid NOT NULL,
            encounter_id uuid,
            authored_by uuid,
            payload json NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            FOREIGN KEY (tenant_id, patient_id) REFERENCES patients(tenant_id, id)
                ON DELETE CASCADE,
            FOREIGN KEY (tenant_id, encounter_id) REFERENCES encounters(tenant_id, id)
                ON DELETE SET NULL (encounter_id),
            FOREIGN KEY (tenant_id, authored_by) REFERENCES users(tenant_id, id)
                ON DELETE SET NULL (authored_by)
        )
        """,
        "CREATE INDEX ix_users_tenant_email ON users (tenant_id, email)",
        "CREATE INDEX ix_patients_tenant_created ON patients (tenant_id, created_at)",
        "CREATE INDEX ix_prescriptions_tenant_patient ON prescriptions (tenant_id, patient_id)",
    ]
    for statement in statements:
        op.execute(statement)

    for table in ("tenants", "users", "patients", "encounters", "prescriptions"):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"""
            CREATE POLICY tenant_isolation_policy ON {table}
            USING (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
            WITH CHECK (tenant_id = nullif(current_setting('app.current_tenant', true), '')::uuid)
        """)
    app_user = os.getenv("POSTGRES_APP_USER", "aponcare_app")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", app_user):
        raise ValueError("POSTGRES_APP_USER must be a valid SQL role name")
    op.execute(
        f'GRANT SELECT, INSERT, UPDATE, DELETE ON '
        f'tenants, users, patients, encounters, prescriptions TO "{app_user}"'
    )


def downgrade() -> None:
    for table in ("prescriptions", "encounters", "patients", "users", "tenants"):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
