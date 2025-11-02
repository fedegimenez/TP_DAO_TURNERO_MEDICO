from datetime import time
from datetime import time
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator
from pydantic.config import ConfigDict

from app.schemas.specialty import SpecialtyOut


class DoctorAvailabilityIn(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    slot_minutes: int = 30

    model_config = ConfigDict(from_attributes=True)

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def valid_time(cls, value: str):
        if isinstance(value, time):
            return value.strftime("%H:%M")
        try:
            time.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("El horario debe tener formato HH:MM") from exc
        return value

class DoctorBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    genero: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    matricula: str

class DoctorCreate(DoctorBase):
    specialty_ids: List[int]
    availability: List[DoctorAvailabilityIn]

class DoctorUpdate(DoctorBase):
    specialty_ids: Optional[List[int]] = None
    availability: Optional[List[DoctorAvailabilityIn]] = None

class DoctorOut(DoctorBase):
    id: int
    activo: bool
    specialties: List[SpecialtyOut]
    availability: List[DoctorAvailabilityIn]
