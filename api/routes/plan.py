from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.DTO.models import InfoPlanCreate
from api.DTO.models_sqlalchemy import

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/crear-infoplan")
def crear_infoplan(data: InfoPlanCreate, db: Session = Depends(get_db)):
    if db.query(InfoPlan).filter_by(IDINFOPLAN=data.idinfoplan).first():
        raise HTTPException(status_code=400, detail="IDINFOPLAN ya existe")

    nuevo_infoplan = InfoPlan(
        IDINFOPLAN=data.idinfoplan,
        NOMBREPLAN=data.nombreplan,
        PRECIO=data.precio,
        NUMSITIOSWEB=data.numsitiosweb,
        NUMBD=data.numbd,
        ALMACENAMIENTO=data.almacenamiento,
        CORREOS=data.correos,
        NUMCERTIFICADOSSSL=data.numcertificadosssl,
        DURACION=data.duracion
    )

    db.add(nuevo_infoplan)
    db.commit()

    return {"message": "InfoPlan creado exitosamente", "idinfoplan": nuevo_infoplan.IDINFOPLAN}
