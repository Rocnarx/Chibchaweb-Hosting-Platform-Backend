from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.DTO.models import CrearPlanRequest
from api.DTO.models_sqlalchemy import InfoPaqueteHosting, Periodicidad, PaqueteHosting

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/CrearPlan")
def crear_plan(data: CrearPlanRequest, db: Session = Depends(get_db)):
    try:
        # Paso 1: Crear InfoPaqueteHosting
        nuevo_info = InfoPaqueteHosting(
            CANTIDADSITIOS=data.cantidadsitios,
            NOMBREPAQUETEHOSTING=data.nombrepaquetehosting,
            BD=data.bd,
            GBENSSD=data.gbenssd,
            CORREOS=data.correos,
            CERTIFICADOSSSLHTTPS=data.certificadosslhttps
        )
        db.add(nuevo_info)
        db.commit()
        db.refresh(nuevo_info)

        # Paso 2: Buscar o crear la periodicidad (por duración)
        periodicidad = db.query(Periodicidad).filter_by(NOMBREPERIODICIDAD=data.nombreperiodicidad).first()
        if not periodicidad:
            periodicidad = Periodicidad(NOMBREPERIODICIDAD=data.nombreperiodicidad)
            db.add(periodicidad)
            db.commit()
            db.refresh(periodicidad)

        # Paso 3: Crear el PaqueteHosting
        nuevo_paquete = PaqueteHosting(
            IDINFOPAQUETEHOSTING=nuevo_info.IDINFOPAQUETEHOSTING,
            IDPERIODICIDAD=periodicidad.IDPERIODICIDAD,
            PRECIOPAQUETE=data.preciopaquete
        )
        db.add(nuevo_paquete)
        db.commit()
        db.refresh(nuevo_paquete)

        return {
            "message": "Plan creado exitosamente",
            "idpaquete": nuevo_paquete.IDPAQUETEHOSTING
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))