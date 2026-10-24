# AponCare HMIS — Phase 1 foundation

This repository contains a starter monorepo for a tenant-aware HMIS API and Next.js application.
It is a development scaffold, not a production-ready or clinically validated system.

## Start locally

1. Copy `.env.example` to `.env` and replace development secrets. Keep `DATABASE_URL` and
   `MIGRATION_DATABASE_URL` passwords synchronized with `POSTGRES_APP_PASSWORD` and
   `POSTGRES_PASSWORD`, respectively.
2. Start services with `docker compose up --build`.
3. Open the frontend at `http://localhost:3000` and the API docs at `http://localhost:8000/docs`.
4. Create the initial organization using `POST /api/v1/auth/signup`; give its tenant ID to patients
   so they can create portal accounts at `/patient-signup`.
5. Front-desk staff can register patients with portal access from the Patients page. Share the
   displayed temporary password with the patient; the patient must change it at first sign-in.

PostgreSQL initialization enables `pgcrypto` and creates a non-superuser application role. The
backend connects with that role; Alembic runs with the separate migration/admin URL. Migrations apply
the schema and forced tenant RLS policies. A dedicated test database must be migrated and
`TEST_DATABASE_URL` must use a non-superuser application role before running `pytest backend/tests`;
PostgreSQL superusers bypass RLS and cannot prove tenant isolation.

## Security notes

- Authenticated tenant IDs are read from signature-verified JWT claims. The database middleware sets
  a transaction-local `app.current_tenant` before route database queries.
- Signup and login establish a scoped transaction explicitly; credentials are verified within that
  tenant's RLS context. The PostgreSQL app role should not be a superuser or have `BYPASSRLS`.
- JWTs are held in frontend memory only and therefore are cleared on a full page reload.
- Configure TLS, secrets, backups, audit trails, retention, privacy controls, clinical validation,
  managed Redis/PostgreSQL, and a production cookie/session strategy before handling real patient data.
- The prescription JSON/PDF implementation is a technical starting point, not a prescribing workflow,
  drug database, interoperability certification, or legal/clinical approval.
