from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.specialty import SpecialtyCreate, SpecialtyUpdate, SpecialtyOut
from app.services.specialty_service import SpecialtyService
from app.api.deps import get_db, get_current_user, require_role

router = APIRouter(prefix="/especialidades", tags=["especialidades"])

@router.get("", response_model=List[SpecialtyOut])
def list_specialties(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return SpecialtyService.list(db)

@router.post("", response_model=SpecialtyOut)
def create_specialty(payload: SpecialtyCreate, db: Session = Depends(get_db),
                     _=Depends(require_role("admin"))):
    return SpecialtyService.create(db, payload.model_dump())

@router.put("/{sid}", response_model=SpecialtyOut)
def update_specialty(sid: int, payload: SpecialtyUpdate, db: Session = Depends(get_db),
                     _=Depends(require_role("admin"))):
    return SpecialtyService.update(db, sid, payload.model_dump(exclude_unset=True))

@router.patch("/{sid}/estado")
def toggle_specialty(sid: int, activa: bool, db: Session = Depends(get_db),
                     _=Depends(require_role("admin"))):
    SpecialtyService.set_estado(db, sid, activa)
    return {"ok": True}
