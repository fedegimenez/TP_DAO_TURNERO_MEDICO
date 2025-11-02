from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.prescription import Prescription


class ConsultationRepo:
    @staticmethod
    def by_patient(db: Session, patient_id: int) -> List[Consultation]:
        stmt = (
            select(Consultation)
            .join(Consultation.appointment)
            .options(
                selectinload(Consultation.appointment).selectinload(Appointment.medico),
                selectinload(Consultation.appointment).selectinload(Appointment.especialidad),
                selectinload(Consultation.prescriptions).selectinload(Prescription.items),
            )
            .where(Appointment.paciente_id == patient_id)
            .order_by(Consultation.created_at.desc())
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_by_appointment(db: Session, appointment_id: int) -> Optional[Consultation]:
        stmt = (
            select(Consultation)
            .where(Consultation.appointment_id == appointment_id)
            .options(selectinload(Consultation.prescriptions).selectinload(Prescription.items))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, appointment: Appointment, **data) -> Consultation:
        consultation = Consultation(appointment=appointment, **data)
        db.add(consultation)
        db.flush()
        return consultation
