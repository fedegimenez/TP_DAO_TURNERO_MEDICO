from datetime import date
from datetime import date
from typing import List, Optional

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, field_validator
from pydantic.config import ConfigDict


class PrescriptionItemIn(BaseModel):
    medicamento: str
    dosis: Optional[str] = None
    frecuencia: Optional[str] = None
    duracion: Optional[str] = None
    indicaciones: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PrescriptionIn(BaseModel):
    fecha_emision: date
    estado: str = "ACTIVA"
    firma_digital: Optional[str] = None
    items: List[PrescriptionItemIn]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, value: str):
        allowed = {"ACTIVA", "ANULADA", "EXPIRADA"}
        if value not in allowed:
            raise ValueError("Estado de receta inválido")
        return value


class PrescriptionOut(PrescriptionIn):
    id: int
