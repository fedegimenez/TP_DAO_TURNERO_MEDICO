from datetime import time
from typing import Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.doctor import Doctor, DoctorAvailability
from app.models.specialty import Specialty


class DoctorRepo:
    @staticmethod
    def list(db: Session) -> List[Doctor]:
        stmt = (
            select(Doctor)
            .options(
                selectinload(Doctor.specialties),
                selectinload(Doctor.availability),
            )
            .order_by(Doctor.apellido, Doctor.nombre)
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def _load_specialties(db: Session, ids: Iterable[int]) -> List[Specialty]:
        if not ids:
            return []
        stmt = select(Specialty).where(Specialty.id.in_(list(ids)))
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def _build_availability(items: Iterable[dict]) -> List[DoctorAvailability]:
        availability: List[DoctorAvailability] = []
        for item in items or []:
            availability.append(
                DoctorAvailability(
                    day_of_week=item["day_of_week"],
                    start_time=time.fromisoformat(item["start_time"]),
                    end_time=time.fromisoformat(item["end_time"]),
                    slot_minutes=item.get("slot_minutes", 30),
                )
            )
        return availability

    @staticmethod
    def _ensure_unique(
        db: Session,
        *,
        dni: str,
        email: Optional[str],
        matricula: str,
        exclude_id: Optional[int] = None,
    ) -> None:
        stmt = select(Doctor).where(Doctor.dni == dni)
        if exclude_id:
            stmt = stmt.where(Doctor.id != exclude_id)
        if db.execute(stmt).scalar_one_or_none():
            raise ValueError("Ya existe un médico con ese DNI")

        if email:
            stmt = select(Doctor).where(Doctor.email == email)
            if exclude_id:
                stmt = stmt.where(Doctor.id != exclude_id)
            if db.execute(stmt).scalar_one_or_none():
                raise ValueError("Ya existe un médico con ese email")

        stmt = select(Doctor).where(Doctor.matricula == matricula)
        if exclude_id:
            stmt = stmt.where(Doctor.id != exclude_id)
        if db.execute(stmt).scalar_one_or_none():
            raise ValueError("Ya existe un médico con esa matrícula")

    @staticmethod
    def create(
        db: Session,
        *,
        specialties: Iterable[int] | None = None,
        availability: Iterable[dict] | None = None,
        **data,
    ) -> Doctor:
        DoctorRepo._ensure_unique(
            db,
            dni=data["dni"],
            email=data.get("email"),
            matricula=data["matricula"],
        )
        doctor = Doctor(**{k: v for k, v in data.items() if k not in {"specialties", "availability"}})
        doctor.specialties = DoctorRepo._load_specialties(db, specialties or [])
        doctor.availability = DoctorRepo._build_availability(availability or [])
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def get(db: Session, did: int) -> Optional[Doctor]:
        return db.get(Doctor, did)

    @staticmethod
    def get_full(db: Session, did: int) -> Optional[Doctor]:
        stmt = (
            select(Doctor)
            .options(
                selectinload(Doctor.specialties),
                selectinload(Doctor.availability),
            )
            .where(Doctor.id == did)
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def update(
        db: Session,
        did: int,
        *,
        specialties: Iterable[int] | None = None,
        availability: Iterable[dict] | None = None,
        **data,
    ) -> Doctor:
        doctor = db.get(Doctor, did)
        if not doctor:
            raise ValueError("Médico inexistente")

        DoctorRepo._ensure_unique(
            db,
            dni=data.get("dni", doctor.dni),
            email=data.get("email", doctor.email),
            matricula=doctor.matricula,
            exclude_id=did,
        )

        for key, value in data.items():
            setattr(doctor, key, value)

        if specialties is not None:
            doctor.specialties = DoctorRepo._load_specialties(db, specialties)
        if availability is not None:
            doctor.availability = DoctorRepo._build_availability(availability)

        db.commit()
        db.refresh(doctor)
        return doctor

    @staticmethod
    def set_estado(db: Session, did: int, activo: bool) -> None:
        doctor = db.get(Doctor, did)
        if not doctor:
            raise ValueError("Médico inexistente")
        doctor.activo = activo
        db.commit()
