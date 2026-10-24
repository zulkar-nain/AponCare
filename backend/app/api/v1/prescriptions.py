from datetime import date
from io import BytesIO
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import authenticated_user_id, require_roles
from app.models import Patient, Prescription

router = APIRouter()


class MedicationItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    medication: str = Field(min_length=1, max_length=200)
    dose: str = Field(min_length=1, max_length=120)
    route: str = Field(default="oral", max_length=80)
    frequency: str = Field(min_length=1, max_length=120)
    duration: str | None = Field(default=None, max_length=120)
    quantity: str | None = Field(default=None, max_length=80)
    refills: int = Field(default=0, ge=0, le=20)


class PrescriptionPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    resourceType: str = "MedicationRequest"
    status: str = "active"
    intent: str = "order"
    authoredOn: date | None = None
    notes: str | None = Field(default=None, max_length=2000)
    medication: list[MedicationItem] = Field(min_length=1, max_length=50)


class PrescriptionCreate(BaseModel):
    patient_id: UUID
    payload: PrescriptionPayload


class PrescriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    patient_id: UUID
    payload: dict[str, Any]


@router.post("", response_model=PrescriptionRead, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    body: PrescriptionCreate,
    claims: dict = Depends(require_roles(["org_admin", "medical_team"])),
    session: AsyncSession = Depends(get_db_session),
) -> PrescriptionRead:
    patient_result = await session.execute(select(Patient).where(Patient.id == body.patient_id))
    if patient_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    prescription = Prescription(
        id=uuid4(),
        tenant_id=UUID(claims["tenant_id"]),
        patient_id=body.patient_id,
        authored_by=authenticated_user_id(claims),
        payload=body.payload.model_dump(mode="json", exclude_none=True),
    )
    session.add(prescription)
    await session.flush()
    return PrescriptionRead.model_validate(prescription)


@router.get("", response_model=list[PrescriptionRead])
async def list_prescriptions(
    claims: dict = Depends(
        require_roles(["org_admin", "staff", "medical_team", "patient_portal"])
    ),
    session: AsyncSession = Depends(get_db_session),
) -> list[PrescriptionRead]:
    query = select(Prescription).order_by(Prescription.created_at.desc())
    if claims["role"] == "patient_portal":
        query = query.join(Patient, Patient.id == Prescription.patient_id).where(
            Patient.user_id == authenticated_user_id(claims)
        )
    result = await session.execute(query)
    return [PrescriptionRead.model_validate(item) for item in result.scalars()]


@router.get("/{prescription_id}/pdf")
async def prescription_pdf(
    prescription_id: UUID,
    claims: dict = Depends(
        require_roles(["org_admin", "staff", "medical_team", "patient_portal"])
    ),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    query = select(Prescription).where(Prescription.id == prescription_id)
    if claims["role"] == "patient_portal":
        query = query.join(Patient, Patient.id == Prescription.patient_id).where(
            Patient.user_id == authenticated_user_id(claims)
        )
    result = await session.execute(query)
    prescription = result.scalar_one_or_none()
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")

    output = BytesIO()
    document = canvas.Canvas(output, pagesize=letter)
    document.setTitle(f"Prescription {prescription.id}")
    document.drawString(72, 740, "AponCare e-Prescription")
    document.drawString(72, 718, f"Prescription ID: {prescription.id}")
    y = 680
    for item in prescription.payload.get("medication", []):
        line = (
            f"{item.get('medication', '')} | Dose: {item.get('dose', '')} | "
            f"Route: {item.get('route', '')} | Frequency: {item.get('frequency', '')}"
        )
        document.drawString(72, y, line[:110])
        y -= 22
        if y < 72:
            document.showPage()
            y = 740
    notes = prescription.payload.get("notes")
    if notes and y >= 72:
        document.drawString(72, y - 8, f"Notes: {notes[:110]}")
    document.save()
    return Response(
        content=output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="prescription-{prescription_id}.pdf"'},
    )
