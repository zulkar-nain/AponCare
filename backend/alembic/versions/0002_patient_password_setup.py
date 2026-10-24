"""Require patients created by front desk to change their temporary password."""

from alembic import op

revision = "0002_patient_password_setup"
down_revision = "0001_initial_rls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN password_change_required "
        "boolean NOT NULL DEFAULT false"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN password_change_required")
