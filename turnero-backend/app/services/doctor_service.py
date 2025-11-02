from sqlalchemy.orm import Session

from app.repositories.doctor_repo import DoctorRepo


class DoctorService:
    @staticmethod
    def list(db: Session):
        return DoctorRepo.list(db)

    @staticmethod
    def create(db: Session, data: dict):
        specialties = data.pop("specialty_ids", [])
        availability = data.pop("availability", [])
        return DoctorRepo.create(db, specialties=specialties, availability=availability, **data)

    @staticmethod
    def update(db: Session, did: int, data: dict):
        data.pop("matricula", None)
        specialties = data.pop("specialty_ids", None)
        availability = data.pop("availability", None)
        return DoctorRepo.update(db, did, specialties=specialties, availability=availability, **data)

    @staticmethod
    def set_estado(db: Session, did: int, activo: bool):
        return DoctorRepo.set_estado(db, did, activo)

    @staticmethod
    def get(db: Session, did: int):
        doctor = DoctorRepo.get_full(db, did)
        if not doctor:
            raise ValueError("Médico inexistente")
        return doctor
