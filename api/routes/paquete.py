from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.DTO.models import CrearPaqueteRequest, PaqueteResponse, InfoPaqueteResponse
from api.DTO.models_sqlalchemy import InfoPaqueteHosting, PaqueteHosting
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/CrearPaquete")
def crear_paquete(data: CrearPaqueteRequest, db: Session = Depends(get_db)):
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

        # Paso 2: Crear el PaqueteHosting con periodicidad directa (sin tabla intermedia)
        nuevo_paquete = PaqueteHosting(
            IDINFOPAQUETEHOSTING=nuevo_info.IDINFOPAQUETEHOSTING,
            PRECIOPAQUETE=data.preciopaquete,
            PERIODICIDAD=data.periodicidad  # varchar(100)
        )
        db.add(nuevo_paquete)
        db.commit()
        db.refresh(nuevo_paquete)

        return {
            "message": "Paquete creado exitosamente",
            "idpaquete": nuevo_paquete.IDPAQUETEHOSTING
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/Paquetes", response_model=List[PaqueteResponse])
def obtener_paquetes(db: Session = Depends(get_db)):
    paquetes = db.query(PaqueteHosting).all()
    if not paquetes:
        raise HTTPException(status_code=404, detail="No hay paquetes disponibles")

    return [
        PaqueteResponse(
            idpaquetehosting=p.IDPAQUETEHOSTING,
            preciopaquete=p.PRECIOPAQUETE,
            periodicidad=p.PERIODICIDAD,
            info=InfoPaqueteResponse(
                cantidadsitios=p.infopaquete.CANTIDADSITIOS,
                nombrepaquetehosting=p.infopaquete.NOMBREPAQUETEHOSTING,
                bd=p.infopaquete.BD,
                gbenssd=p.infopaquete.GBENSSD,
                correos=p.infopaquete.CORREOS,
                certificadosslhttps=p.infopaquete.CERTIFICADOSSSLHTTPS
            )
        )
        for p in paquetes
    ]