from datetime import datetime, date

from sqlalchemy.orm import Session

from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.patient_repo import PatientRepo


def _parse_birthdate(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("La fecha de nacimiento debe tener formato YYYY-MM-DD") from exc


class PatientService:
    @staticmethod
    def list(db: Session):
        return PatientRepo.list(db)

    @staticmethod
    def create(db: Session, data: dict):
        birth = _parse_birthdate(data["fecha_nacimiento"])
        if birth > datetime.now().date():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        data["fecha_nacimiento"] = birth
        return PatientRepo.create(db, **data)

    @staticmethod
    def update(db: Session, pid: int, data: dict):
        if "fecha_nacimiento" in data:
            birth = _parse_birthdate(data["fecha_nacimiento"])
            if birth > datetime.now().date():
                raise ValueError("La fecha de nacimiento no puede ser futura")
            data["fecha_nacimiento"] = birth
        data.pop("dni", None)
        return PatientRepo.update(db, pid, **data)

    @staticmethod
    def set_estado(db: Session, pid: int, activo: bool):
        return PatientRepo.set_estado(db, pid, activo)

    @staticmethod
    def get(db: Session, pid: int):
        patient = PatientRepo.get(db, pid)
        if not patient:
            raise ValueError("Paciente inexistente")
        return patient
