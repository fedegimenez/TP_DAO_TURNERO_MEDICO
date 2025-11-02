from datetime import datetime
from sqlalchemy.orm import Session

from app.models.appointment import TurnoEstado
from app.models.prescription import Prescription, PrescriptionItem
from app.repositories.appointment_repo import AppointmentRepo
from app.repositories.consultation_repo import ConsultationRepo
from app.schemas.consultation import ConsultationCreate
from app.schemas.prescription import PrescriptionIn


class ConsultationService:
    @staticmethod
    def registrar(db: Session, appointment_id: int, payload: ConsultationCreate):
        appointment = AppointmentRepo.get(db, appointment_id)
        if not appointment:
            raise ValueError("Turno inexistente")
        if appointment.estado == TurnoEstado.Cancelado:
            raise ValueError("El turno está cancelado")
        if appointment.fecha > datetime.now():
            raise ValueError("Solo se pueden registrar consultas de turnos ya realizados")
        if ConsultationRepo.get_by_appointment(db, appointment_id):
            raise ValueError("El turno ya tiene una consulta registrada")

        data = payload.model_dump(exclude={"receta"}, exclude_none=True)
        with db.begin():
            if appointment.estado != TurnoEstado.Atendido:
                appointment.estado = TurnoEstado.Atendido
            consultation = ConsultationRepo.create(db, appointment, **data)
            if payload.receta:
                ConsultationService._crear_receta(db, consultation.id, payload.receta)
        db.refresh(consultation)
        return consultation

    @staticmethod
    def _crear_receta(db: Session, consultation_id: int, receta: PrescriptionIn):
        prescription = Prescription(
            consultation_id=consultation_id,
            fecha_emision=receta.fecha_emision,
            estado=receta.estado,
            firma_digital=receta.firma_digital,
        )
        db.add(prescription)
        db.flush()
        for item in receta.items:
            db.add(
                PrescriptionItem(
                    prescription_id=prescription.id,
                    medicamento=item.medicamento,
                    dosis=item.dosis,
                    frecuencia=item.frecuencia,
                    duracion=item.duracion,
                    indicaciones=item.indicaciones,
                )
            )

    @staticmethod
    def historial_paciente(db: Session, paciente_id: int):
        return ConsultationRepo.by_patient(db, paciente_id)

    @staticmethod
    def detalle_turno(db: Session, appointment_id: int):
        return ConsultationRepo.get_by_appointment(db, appointment_id)
