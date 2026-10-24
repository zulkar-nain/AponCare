import secrets
from datetime import date
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import authenticated_user_id, require_roles
from app.core.security import hash_password
from app.models import Patient, User

router = APIRouter()


class PatientCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    date_of_birth: date | None = None
    sex: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, max_length=64)


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    full_name: str
    date_of_birth: date | None
    sex: str | None
    phone: str | None


class AssistedPortalSignupRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    date_of_birth: date | None = None
    sex: str | None = Field(default=None, max_length=32)
    phone: str | None = Field(default=None, max_length=64)


class AssistedPortalSignupResponse(BaseModel):
    patient: PatientRead
    email: EmailStr
    temporary_password: str
    password_change_required: bool = True


@router.get("", response_model=list[PatientRead])
async def list_patients(
    claims: dict = Depends(
        require_roles(["org_admin", "staff", "medical_team", "patient_portal"])
    ),
    session: AsyncSession = Depends(get_db_session),
) -> list[PatientRead]:
    query = select(Patient).order_by(Patient.created_at.desc())
    if claims["role"] == "patient_portal":
        query = query.where(Patient.user_id == authenticated_user_id(claims))
    result = await session.execute(query)
    return [PatientRead.model_validate(patient) for patient in result.scalars()]


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
async def create_patient(
    body: PatientCreate,
    claims: dict = Depends(require_roles(["org_admin", "staff", "medical_team"])),
    session: AsyncSession = Depends(get_db_session),
) -> PatientRead:
    patient = Patient(
        id=uuid4(),
        tenant_id=UUID(claims["tenant_id"]),
        full_name=body.full_name,
        date_of_birth=body.date_of_birth,
        sex=body.sex,
        phone=body.phone,
    )
    session.add(patient)
    await session.flush()
    return PatientRead.model_validate(patient)


@router.post(
    "/register-portal",
    response_model=AssistedPortalSignupResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_patient_portal_account(
    body: AssistedPortalSignupRequest,
    claims: dict = Depends(require_roles(["org_admin", "staff"])),
    session: AsyncSession = Depends(get_db_session),
) -> AssistedPortalSignupResponse:
    tenant_id = UUID(claims["tenant_id"])
    email = body.email.lower()
    existing = await session.execute(
        select(User.id).where(User.tenant_id == tenant_id, User.email == email)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Unable to register with those details")

    temporary_password = f"Apc-{secrets.token_urlsafe(18)}"
    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=body.full_name,
        password_hash=hash_password(temporary_password),
        role="patient_portal",
        password_change_required=True,
    )
    patient = Patient(
        id=uuid4(),
        tenant_id=tenant_id,
        user_id=user.id,
        full_name=body.full_name,
        date_of_birth=body.date_of_birth,
        sex=body.sex,
        phone=body.phone,
    )
    session.add(user)
    await session.flush()
    session.add(patient)
    await session.flush()
    return AssistedPortalSignupResponse(
        patient=PatientRead.model_validate(patient),
        email=email,
        temporary_password=temporary_password,
    )


@router.get("/{patient_id}", response_model=PatientRead)
async def get_patient(
    patient_id: UUID,
    claims: dict = Depends(
        require_roles(["org_admin", "staff", "medical_team", "patient_portal"])
    ),
    session: AsyncSession = Depends(get_db_session),
) -> PatientRead:
    query = select(Patient).where(Patient.id == patient_id)
    if claims["role"] == "patient_portal":
        query = query.where(Patient.user_id == authenticated_user_id(claims))
    result = await session.execute(query)
    patient = result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientRead.model_validate(patient)
