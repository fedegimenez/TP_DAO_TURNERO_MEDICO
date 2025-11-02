from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_current_user, get_db
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.schemas.consultation import ConsultationCreate, ConsultationOut
from app.schemas.reminder import ReminderCreate, ReminderOut
from app.services.appointment_service import AppointmentService
from app.services.consultation_service import ConsultationService
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/turnos", tags=["turnos"])

@router.get("", response_model=List[AppointmentOut])
def list_turnos(medico_id: Optional[int] = None, desde: Optional[str] = None, hasta: Optional[str] = None,
                db: Session = Depends(get_db), _=Depends(get_current_user)):
    return AppointmentService.list(db, medico_id, desde, hasta)

@router.get("/{tid}", response_model=AppointmentOut)
def get_turno(tid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return AppointmentService.get(db, tid)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@router.post("", response_model=AppointmentOut)
def create_turno(payload: AppointmentCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return AppointmentService.create(db, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tid}", response_model=AppointmentOut)
def update_turno(tid: int, payload: AppointmentUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return AppointmentService.update(db, tid, payload.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{tid}/cancelar")
def cancelar_turno(tid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        AppointmentService.cancelar(db, tid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True}

@router.post("/{tid}/atender")
def atender_turno(tid: int, receta_url: str | None = None, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        AppointmentService.atender(db, tid, receta_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True}

@router.get("/disponibles")
def turnos_disponibles(medico_id: int, fecha: str,
                       duracion_min: int = 30, inicio: str = "09:00", fin: str = "17:00",
                       db: Session = Depends(get_db), _=Depends(get_current_user)):
    # fecha = "YYYY-MM-DD"
    try:
        return AppointmentService.disponibles(db, medico_id, fecha, duracion_min, inicio, fin)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{tid}/consulta", response_model=ConsultationOut)
def registrar_consulta(tid: int, payload: ConsultationCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        consulta = ConsultationService.registrar(db, tid, payload)
        return consulta
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{tid}/consulta", response_model=Optional[ConsultationOut])
def obtener_consulta(tid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ConsultationService.detalle_turno(db, tid)


@router.get("/paciente/{pid}/historial", response_model=List[ConsultationOut])
def historial_paciente(pid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ConsultationService.historial_paciente(db, pid)


@router.post("/{tid}/recordatorios", response_model=ReminderOut)
def programar_recordatorio(tid: int, payload: ReminderCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return ReminderService.programar(db, tid, payload.canal, payload.programado_para)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/{tid}/recordatorios", response_model=List[ReminderOut])
def listar_recordatorios(tid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return ReminderService.listar(db, tid)
