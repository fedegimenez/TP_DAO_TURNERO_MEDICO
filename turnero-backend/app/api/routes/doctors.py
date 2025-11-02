from fastapi import APIRouter, Depends, HTTPException
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.services.doctor_service import DoctorService

router = APIRouter(prefix="/medicos", tags=["medicos"])


@router.get("", response_model=List[DoctorOut])
def list_doctors(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return DoctorService.list(db)


@router.get("/{did}", response_model=DoctorOut)
def get_doctor(did: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return DoctorService.get(db, did)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=DoctorOut)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return DoctorService.create(db, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/{did}", response_model=DoctorOut)
def update_doctor(did: int, payload: DoctorUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        return DoctorService.update(db, did, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.patch("/{did}/estado")
def toggle_doctor(did: int, activo: bool, db: Session = Depends(get_db), _=Depends(get_current_user)):
    try:
        DoctorService.set_estado(db, did, activo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"ok": True}
