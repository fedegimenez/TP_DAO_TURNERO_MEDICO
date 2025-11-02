from __future__ import annotations

from datetime import datetime, timedelta, time
from typing import Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment, TurnoEstado
from app.models.doctor import Doctor, DoctorAvailability
from app.models.patient import Patient
from app.models.specialty import Specialty
from app.repositories.appointment_repo import AppointmentRepo

FMT = "%Y-%m-%dT%H:%M"


def _parse_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Formato de fecha inválido. Usar YYYY-MM-DDTHH:MM") from exc


def _time_in_availability(avail: DoctorAvailability, start: datetime, duration: int) -> bool:
    start_time = start.time()
    end_time = (start + timedelta(minutes=duration)).time()
    return (
        avail.day_of_week == start.weekday()
        and avail.start_time <= start_time
        and end_time <= avail.end_time
    )


class AppointmentService:
    @staticmethod
    def list(db: Session, medico_id: Optional[int], desde: Optional[str], hasta: Optional[str]):
        desde_dt = _parse_datetime(desde) if desde else None
        hasta_dt = _parse_datetime(hasta) if hasta else None
        return AppointmentRepo.list(db, medico_id, desde_dt, hasta_dt)

    @staticmethod
    def get(db: Session, tid: int):
        ap = AppointmentRepo.get(db, tid)
        if not ap:
            raise ValueError("Turno inexistente")
        return ap

    @staticmethod
    def _validate_slot(
        db: Session,
        doctor_id: int,
        patient_id: int,
        specialty_id: int,
        start: datetime,
        duration: int,
        exclude_id: Optional[int] = None,
    ) -> None:
        if start < datetime.now():
            raise ValueError("La fecha del turno debe ser futura")
        if duration <= 0:
            raise ValueError("La duración debe ser mayor a 0")

        doctor: Doctor | None = db.get(Doctor, doctor_id)
        if not doctor or not doctor.activo:
            raise ValueError("El médico no está activo")
        if not doctor.specialties:
            raise ValueError("El médico no tiene especialidades asignadas")
        if specialty_id not in {s.id for s in doctor.specialties}:
            raise ValueError("La especialidad seleccionada no corresponde al médico")

        patient = db.get(Patient, patient_id)
        if not patient or not patient.activo:
            raise ValueError("El paciente no está activo")

        # Validar disponibilidad
        weekday = start.weekday()
        availabilities = [a for a in doctor.availability if a.day_of_week == weekday]
        if not availabilities:
            raise ValueError("El médico no posee disponibilidad configurada para ese día")

        slot_ok = any(_time_in_availability(av, start, duration) for av in availabilities)
        if not slot_ok:
            raise ValueError("El horario no se encuentra dentro de la disponibilidad del médico")

        if AppointmentRepo.overlaps(db, doctor_id, patient_id, start, duration, exclude_id):
            raise ValueError("Existe un solapamiento con otro turno del médico o del paciente")

    @staticmethod
    def create(db: Session, data: dict):
        start = _parse_datetime(data["fecha"])
        duration = data.get("duracion_min", 30)
        AppointmentService._validate_slot(
            db,
            data["medico_id"],
            data["paciente_id"],
            data["especialidad_id"],
            start,
            duration,
        )
        data["fecha"] = start
        return AppointmentRepo.create(db, **data)

    @staticmethod
    def update(db: Session, tid: int, data: dict):
        existing = AppointmentRepo.get(db, tid)
        if not existing:
            raise ValueError("Turno inexistente")

        start = _parse_datetime(data["fecha"]) if "fecha" in data else existing.fecha
        duration = data.get("duracion_min", existing.duracion_min)
        doctor_id = data.get("medico_id", existing.medico_id)
        patient_id = data.get("paciente_id", existing.paciente_id)
        specialty_id = data.get("especialidad_id", existing.especialidad_id)

        AppointmentService._validate_slot(
            db,
            doctor_id,
            patient_id,
            specialty_id,
            start,
            duration,
            exclude_id=tid,
        )

        data["fecha"] = start
        return AppointmentRepo.update(db, tid, **data)

    @staticmethod
    def cancelar(db: Session, tid: int):
        appointment = AppointmentRepo.get(db, tid)
        if not appointment:
            raise ValueError("Turno inexistente")
        if appointment.estado in {TurnoEstado.Cancelado, TurnoEstado.Atendido}:
            raise ValueError("El turno no puede cancelarse")
        if appointment.fecha <= datetime.now():
            raise ValueError("Solo se pueden cancelar turnos futuros")
        return AppointmentRepo.cancel(db, tid)

    @staticmethod
    def atender(db: Session, tid: int, receta_url: Optional[str] = None):
        appointment = AppointmentRepo.get(db, tid)
        if not appointment:
            raise ValueError("Turno inexistente")
        if appointment.estado in {TurnoEstado.Cancelado, TurnoEstado.Atendido}:
            raise ValueError("El turno no puede marcarse como atendido")
        if appointment.fecha > datetime.now():
            raise ValueError("Solo se pueden cerrar turnos cuya fecha ya ocurrió")
        return AppointmentRepo.atender(db, tid, receta_url)

    @staticmethod
    def resumen(db: Session):
        total_pacientes = db.scalar(select(func.count(Patient.id))) or 0
        total_medicos = db.scalar(select(func.count(Doctor.id))) or 0
        today = datetime.now()
        inicio = datetime.combine(today.date(), time.min)
        fin = datetime.combine(today.date(), time.max)
        turnos_hoy = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.fecha >= inicio,
                Appointment.fecha <= fin,
                Appointment.estado != TurnoEstado.Cancelado,
            )
        ) or 0
        return {"pacientes": total_pacientes, "medicos": total_medicos, "turnos_hoy": turnos_hoy}

    @staticmethod
    def reportes_por_medico(db: Session, desde: Optional[str], hasta: Optional[str]):
        desde_dt = _parse_datetime(desde) if desde else None
        hasta_dt = _parse_datetime(hasta) if hasta else None

        appt = select(Appointment.medico_id, func.count(Appointment.id).label("total"))
        if desde_dt:
            appt = appt.where(Appointment.fecha >= desde_dt)
        if hasta_dt:
            appt = appt.where(Appointment.fecha <= hasta_dt)
        appt = appt.group_by(Appointment.medico_id).subquery()

        stmt = (
            select(
                Doctor.apellido,
                Doctor.nombre,
                func.coalesce(appt.c.total, 0),
            )
            .outerjoin(appt, appt.c.medico_id == Doctor.id)
            .order_by(Doctor.apellido, Doctor.nombre)
        )

        rows = db.execute(stmt).all()
        return [
            {"medico": f"{a}, {n}", "fecha": f"{desde or '-'}→{hasta or '-'}", "total": int(t or 0)}
            for a, n, t in rows
        ]

    @staticmethod
    def reportes_por_especialidad(db: Session):
        appt = (
            select(Appointment.especialidad_id, func.count(Appointment.id).label("total"))
            .group_by(Appointment.especialidad_id)
            .subquery()
        )
        stmt = (
            select(
                Specialty.nombre,
                func.coalesce(appt.c.total, 0),
            )
            .outerjoin(appt, appt.c.especialidad_id == Specialty.id)
            .order_by(Specialty.nombre)
        )
        rows = db.execute(stmt).all()
        return [{"especialidad": n, "total": int(t or 0)} for n, t in rows]

    @staticmethod
    def pacientes_atendidos(db: Session, desde: str, hasta: str, medico_id: Optional[int] = None, especialidad_id: Optional[int] = None):
        if not desde or not hasta:
            raise ValueError("Debe indicar rango de fechas")
        desde_dt = _parse_datetime(f"{desde}T00:00")
        hasta_dt = _parse_datetime(f"{hasta}T23:59")
        stmt = (
            select(
                Appointment.fecha,
                Patient.apellido.label("pac_apellido"),
                Patient.nombre.label("pac_nombre"),
                Doctor.apellido.label("med_apellido"),
                Doctor.nombre.label("med_nombre"),
                Specialty.nombre.label("especialidad"),
            )
            .join(Patient, Patient.id == Appointment.paciente_id)
            .join(Doctor, Doctor.id == Appointment.medico_id)
            .join(Specialty, Specialty.id == Appointment.especialidad_id)
            .where(
                Appointment.estado == TurnoEstado.Atendido,
                Appointment.fecha >= desde_dt,
                Appointment.fecha <= hasta_dt,
            )
            .order_by(Appointment.fecha)
        )
        if medico_id:
            stmt = stmt.where(Appointment.medico_id == medico_id)
        if especialidad_id:
            stmt = stmt.where(Appointment.especialidad_id == especialidad_id)
        rows = db.execute(stmt).all()
        return [
            {
                "fecha": fecha.strftime(FMT),
                "paciente": f"{pac_apellido}, {pac_nombre}",
                "medico": f"{med_apellido}, {med_nombre}",
                "especialidad": esp,
            }
            for fecha, pac_apellido, pac_nombre, med_apellido, med_nombre, esp in rows
        ]

    @staticmethod
    def asistencia_vs_inasistencia(db: Session, desde: str, hasta: str):
        if not desde or not hasta:
            raise ValueError("Debe indicar rango de fechas")
        desde_dt = _parse_datetime(f"{desde}T00:00")
        hasta_dt = _parse_datetime(f"{hasta}T23:59")
        asistencias = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.estado == TurnoEstado.Atendido,
                Appointment.fecha >= desde_dt,
                Appointment.fecha <= hasta_dt,
            )
        ) or 0
        reserved_past = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.estado == TurnoEstado.Reservado,
                Appointment.fecha >= desde_dt,
                Appointment.fecha <= hasta_dt,
                Appointment.fecha < datetime.now(),
            )
        ) or 0
        cancelados = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.estado == TurnoEstado.Cancelado,
                Appointment.fecha >= desde_dt,
                Appointment.fecha <= hasta_dt,
            )
        ) or 0
        inasistencias = reserved_past + cancelados
        return {
            "asistencias": asistencias,
            "inasistencias": inasistencias,
            "cancelados": cancelados,
        }

    @staticmethod
    def disponibles(
        db: Session,
        medico_id: int,
        fecha: str,
        duracion_min: int = 30,
        inicio: str | None = None,
        fin: str | None = None,
    ) -> List[Dict]:
        doctor: Doctor | None = db.get(Doctor, medico_id)
        if not doctor:
            return []

        day = datetime.fromisoformat(f"{fecha}T00:00")
        weekday = day.weekday()
        availabilities = [a for a in doctor.availability if a.day_of_week == weekday]
        if not availabilities:
            return []

        start_of_day = datetime.combine(day.date(), time.min)
        end_of_day = datetime.combine(day.date(), time.max)
        busy = AppointmentRepo.list(db, medico_id=medico_id, desde=start_of_day, hasta=end_of_day)

        slots: List[Dict] = []
        for av in availabilities:
            av_start = datetime.combine(day.date(), av.start_time)
            av_end = datetime.combine(day.date(), av.end_time)
            if inicio:
                custom_start = datetime.combine(day.date(), datetime.strptime(inicio, "%H:%M").time())
                av_start = max(av_start, custom_start)
            if fin:
                custom_end = datetime.combine(day.date(), datetime.strptime(fin, "%H:%M").time())
                av_end = min(av_end, custom_end)
            current = av_start
            step = timedelta(minutes=duracion_min)
            while current + step <= av_end:
                slot_end = current + step
                overlap = False
                for ap in busy:
                    if ap.estado == TurnoEstado.Cancelado:
                        continue
                    ap_end = ap.fecha + timedelta(minutes=ap.duracion_min)
                    if ap.fecha < slot_end and current < ap_end:
                        overlap = True
                        break
                if not overlap:
                    slots.append(
                        {
                            "iso": current.strftime(FMT),
                            "inicio": current.strftime("%H:%M"),
                            "fin": slot_end.strftime("%H:%M"),
                        }
                    )
                current += step
        return slots
