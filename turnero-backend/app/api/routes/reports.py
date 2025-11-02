from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get("/turnos-medico")
def rpt_turnos_medico(
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return AppointmentService.reportes_por_medico(db, desde, hasta)


@router.get("/turnos-especialidad")
def rpt_turnos_especialidad(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return AppointmentService.reportes_por_especialidad(db)


@router.get("/pacientes-atendidos")
def rpt_pacientes_atendidos(
    desde: str,
    hasta: str,
    medico_id: Optional[int] = None,
    especialidad_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    try:
        return AppointmentService.pacientes_atendidos(db, desde, hasta, medico_id, especialidad_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/asistencia")
def rpt_asistencia(desde: str, hasta: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return AppointmentService.asistencia_vs_inasistencia(db, desde, hasta)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/resumen")
def resumen(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return AppointmentService.resumen(db)
