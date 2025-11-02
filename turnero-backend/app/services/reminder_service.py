from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.appointment import TurnoEstado
from app.models.reminder import Reminder
from app.repositories.appointment_repo import AppointmentRepo
from app.repositories.reminder_repo import ReminderRepo


class ReminderService:
    @staticmethod
    def programar(db: Session, appointment_id: int, canal: str, programado_para: datetime) -> Reminder:
        appointment = AppointmentRepo.get(db, appointment_id)
        if not appointment:
            raise ValueError("Turno inexistente")
        if appointment.estado != TurnoEstado.Reservado:
            raise ValueError("Solo se permiten recordatorios para turnos reservados")
        if programado_para > appointment.fecha - timedelta(hours=24):
            raise ValueError("El recordatorio debe programarse con al menos 24hs de anticipación")
        if canal.upper() not in {"EMAIL", "SMS", "PUSH"}:
            raise ValueError("Canal inválido")
        return ReminderRepo.create(
            db,
            appointment_id=appointment_id,
            canal=canal.upper(),
            programado_para=programado_para,
            estado="PENDIENTE",
        )

    @staticmethod
    def listar(db: Session, appointment_id: int):
        return ReminderRepo.upcoming_for_appointment(db, appointment_id)
