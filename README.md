# AponCare

### Care coordination, made clearer.

AponCare is a multi-tenant healthcare management system that brings patient records, clinical
encounters, and prescriptions together in one workspace for care teams and patients.

## What you can do

- **Manage patient records** with organization-scoped access and patient portal accounts.
- **Coordinate care** with clinical encounter records and role-aware workflows.
- **Create prescriptions** with structured, FHIR-inspired medication requests and printable PDFs.
- **Register patients** through self-signup or front-desk assisted onboarding.
- **Protect access** with tenant-isolated PostgreSQL row-level security, role-based permissions,
  JWT sessions, TOTP two-factor authentication, and Redis-backed rate limiting.
- **See what’s happening** with BetterStack log integration.

## Built with

**FastAPI · Python · PostgreSQL · Redis · Next.js · TypeScript · Tailwind CSS**

## Get started

1. Copy `.env.example` to `.env` and set your local secrets and database passwords.
2. Start the services: `docker compose up --build`
3. Visit the app at [localhost:3000](http://localhost:3000) or API docs at
   [localhost:8000/docs](http://localhost:8000/docs).
4. Create an organization with `POST /api/v1/auth/signup`. Share its tenant ID with patients so
   they can register at `/patient-signup`.

Front-desk staff can also create patient portal accounts from the Patients page. The patient receives
a temporary password and must change it at first sign-in.

## Verify tenant isolation

Run the RLS integration test against a migrated test database using a non-superuser role:

```powershell
$env:TEST_DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/aponcare_test"
pytest backend/tests
```
