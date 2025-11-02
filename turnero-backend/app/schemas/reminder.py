from datetime import datetime
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator
from pydantic.config import ConfigDict


class ReminderCreate(BaseModel):
    canal: str
    programado_para: datetime

    @field_validator("canal")
    @classmethod
    def normalize_canal(cls, value: str):
        value = value.upper()
        if value not in {"EMAIL", "SMS", "PUSH"}:
            raise ValueError("Canal inválido")
        return value


class ReminderOut(BaseModel):
    id: int
    canal: str
    programado_para: datetime
    enviado_en: Optional[datetime] = None
    estado: str
    error_msg: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
