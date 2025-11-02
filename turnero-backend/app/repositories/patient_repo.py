from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient


class PatientRepo:
    @staticmethod
    def list(db: Session) -> List[Patient]:
        stmt = select(Patient).order_by(Patient.apellido, Patient.nombre)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def _ensure_unique(
        db: Session,
        *,
        dni: str,
        email: Optional[str],
        exclude_id: Optional[int] = None,
    ) -> None:
        stmt = select(Patient).where(Patient.dni == dni)
        if exclude_id:
            stmt = stmt.where(Patient.id != exclude_id)
        if db.execute(stmt).scalar_one_or_none():
            raise ValueError("Ya existe un paciente con ese DNI")

        if email:
            stmt = select(Patient).where(Patient.email == email)
            if exclude_id:
                stmt = stmt.where(Patient.id != exclude_id)
            if db.execute(stmt).scalar_one_or_none():
                raise ValueError("Ya existe un paciente con ese email")

    @staticmethod
    def create(db: Session, **data) -> Patient:
        PatientRepo._ensure_unique(db, dni=data["dni"], email=data.get("email"))
        obj = Patient(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, pid: int) -> Optional[Patient]:
        return db.get(Patient, pid)

    @staticmethod
    def update(db: Session, pid: int, **data) -> Patient:
        obj = db.get(Patient, pid)
        if not obj:
            raise ValueError("Paciente inexistente")
        PatientRepo._ensure_unique(
            db,
            dni=data.get("dni", obj.dni),
            email=data.get("email", obj.email),
            exclude_id=pid,
        )
        for k, v in data.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def set_estado(db: Session, pid: int, activo: bool) -> None:
        obj = db.get(Patient, pid)
        if not obj:
            raise ValueError("Paciente inexistente")
        obj.activo = activo
        db.commit()
