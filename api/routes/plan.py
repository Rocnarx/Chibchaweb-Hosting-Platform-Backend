from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.DTO.models_sqlalchemy import Cuenta, Plan
from ..DAO.database import SessionLocal
from api.DTO.models import MiPlanResponse, CambiarPlanRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/MiPlan", response_model=MiPlanResponse)
def obtener_mi_plan(idcuenta: str = Query(...), db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter_by(IDCUENTA=idcuenta).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    plan = cuenta.PLAN_REL
    if not plan:
        raise HTTPException(status_code=404, detail="La cuenta no tiene un plan asociado")

    return MiPlanResponse(
        idplan=plan.IDPLAN,
        nombreplan=plan.NOMBREPLAN,
        comision=plan.COMISION
    )

@router.put("/CambiarPlan")
def cambiar_plan(data: CambiarPlanRequest, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter_by(IDCUENTA=data.idcuenta).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    plan = db.query(Plan).filter_by(IDPLAN=data.idplan).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    cuenta.IDPLAN = data.idplan
    db.commit()
    db.refresh(cuenta)

    return {
        "message": f"Plan actualizado exitosamente para la cuenta {data.idcuenta}",
        "nuevo_plan": plan.NOMBREPLAN
    }