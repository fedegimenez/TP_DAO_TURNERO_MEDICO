from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, TurnoEstado

class AppointmentRepo:
    @staticmethod
    def list(
        db: Session,
        medico_id: int | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> List[Appointment]:
        stmt = select(Appointment)
        if medico_id:
            stmt = stmt.where(Appointment.medico_id == medico_id)
        if desde:
            stmt = stmt.where(Appointment.fecha >= desde)
        if hasta:
            stmt = stmt.where(Appointment.fecha <= hasta)
        stmt = stmt.order_by(Appointment.fecha)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create(db: Session, **data) -> Appointment:
        obj = Appointment(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def get(db: Session, tid: int) -> Optional[Appointment]:
        return db.get(Appointment, tid)

    @staticmethod
    def update(db: Session, tid: int, **data) -> Appointment:
        obj = db.get(Appointment, tid)
        for k, v in data.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def cancel(db: Session, tid: int):
        obj = db.get(Appointment, tid)
        obj.estado = TurnoEstado.Cancelado
        db.commit()

    @staticmethod
    def atender(db: Session, tid: int, receta_url: str | None = None, *, auto_commit: bool = True):
        obj = db.get(Appointment, tid)
        obj.estado = TurnoEstado.Atendido
        if receta_url:
            obj.receta_url = receta_url
        if auto_commit:
            db.commit()

    @staticmethod
    def overlaps(
        db: Session,
        doctor_id: int,
        patient_id: int,
        inicio: datetime,
        duracion: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        fin = inicio + timedelta(minutes=duracion)
        stmt = (
            select(Appointment)
            .where(
                Appointment.estado != TurnoEstado.Cancelado,
                or_(
                    Appointment.medico_id == doctor_id,
                    Appointment.paciente_id == patient_id,
                ),
            )
            .order_by(Appointment.fecha)
        )
        if exclude_id:
            stmt = stmt.where(Appointment.id != exclude_id)

        candidates = db.execute(stmt).scalars().all()
        for ap in candidates:
            ap_end = ap.fecha + timedelta(minutes=ap.duracion_min)
            if ap.fecha < fin and inicio < ap_end:
                return True
        return False
