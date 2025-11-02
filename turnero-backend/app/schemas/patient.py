from datetime import date
from pydantic import BaseModel, EmailStr, field_validator
from pydantic.config import ConfigDict
from typing import Optional


class PatientBase(BaseModel):
    nombre: str
    apellido: str
    dni: str
    fecha_nacimiento: str
    genero: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    obra_social: Optional[str] = None
    nro_afiliado: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("fecha_nacimiento", mode="before")
    @classmethod
    def valid_date(cls, v: str):
        if isinstance(v, date):
            return v.strftime("%Y-%m-%d")
        assert len(v) == 10 and v[4] == "-" and v[7] == "-", "fecha_nacimiento debe ser YYYY-MM-DD"
        return v


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientOut(PatientBase):
    id: int
    activo: bool
