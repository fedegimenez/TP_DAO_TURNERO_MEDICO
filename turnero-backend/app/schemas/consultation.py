from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.schemas.prescription import PrescriptionIn, PrescriptionOut


class ConsultationCreate(BaseModel):
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    diagnostico: Optional[str] = None
    indicaciones: Optional[str] = None
    receta: Optional[PrescriptionIn] = None


class ConsultationOut(BaseModel):
    id: int
    appointment_id: int
    created_at: datetime
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    diagnostico: Optional[str] = None
    indicaciones: Optional[str] = None
    receta: Optional[PrescriptionOut] = None

    model_config = ConfigDict(from_attributes=True)
