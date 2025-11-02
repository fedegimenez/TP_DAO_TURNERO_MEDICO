from fastapi import APIRouter, Depends, HTTPException
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter(prefix="/pacientes", tags=["pacientes"])


@router.get("", response_model=List[PatientOut])
def list_pacientes(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return PatientService.list(db)


@router.get("/{pid}", response_model=PatientOut)
def get_paciente(pid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return PatientService.get(db, pid)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=PatientOut)
def create_paciente(payload: PatientCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return PatientService.create(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{pid}", response_model=PatientOut)
def update_paciente(pid: int, payload: PatientUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return PatientService.update(db, pid, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{pid}/estado")
def toggle_paciente(pid: int, activo: bool, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        PatientService.set_estado(db, pid, activo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"ok": True}
