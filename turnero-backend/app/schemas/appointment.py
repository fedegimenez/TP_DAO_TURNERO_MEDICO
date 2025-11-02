from datetime import datetime
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_serializer, field_validator
from pydantic.config import ConfigDict

TurnoEstado = Literal["Reservado", "Cancelado", "Reprogramado", "Atendido"]


class AppointmentBase(BaseModel):
    paciente_id: int
    medico_id: int
    especialidad_id: int
    fecha: datetime
    duracion_min: int = 30
    receta_url: Optional[str] = None

    @field_validator("fecha", mode="before")
    @classmethod
    def parse_fecha(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("La fecha debe tener formato YYYY-MM-DDTHH:MM") from exc

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("fecha")
    def serialize_fecha(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M")


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    fecha: Optional[datetime] = None
    duracion_min: Optional[int] = None
    estado: Optional[TurnoEstado] = None
    receta_url: Optional[str] = None
    paciente_id: Optional[int] = None
    medico_id: Optional[int] = None
    especialidad_id: Optional[int] = None

    @field_validator("fecha", mode="before")
    @classmethod
    def parse_fecha(cls, value):
        if value is None:
            return value
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("La fecha debe tener formato YYYY-MM-DDTHH:MM") from exc


class AppointmentOut(AppointmentBase):
    id: int
    estado: TurnoEstado
