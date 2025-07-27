from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import random
from api.database import SessionLocal
from api.models import MetodoPagoCuentaCreate, TarjetaCreate
from api.models_sqlalchemy import MetodoPagoCuenta, Tarjeta

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tarjeta")
def registrar_tarjeta(tarjeta_data: TarjetaCreate, db: Session = Depends(get_db)):
    nueva_tarjeta = Tarjeta(
        idtipotarjeta=tarjeta_data.idtipotarjeta,
        numerotarjeta=tarjeta_data.numerotarjeta,
        ccv=tarjeta_data.ccv,
        fechavto=tarjeta_data.fechavto
    )

    db.add(nueva_tarjeta)
    db.commit()
    db.refresh(nueva_tarjeta)  # Obtener el ID autogenerado

    return {
        "mensaje": "Tarjeta registrada correctamente",
        "idtarjeta": nueva_tarjeta.idtarjeta
    }

@router.post("/metodopago")
def agregar_metodo_pago(data: MetodoPagoCuentaCreate, db: Session = Depends(get_db)):
    metodo = MetodoPagoCuenta(
        idmetodopagocuenta=data.idmetodopagocuenta,
        idtarjeta=data.idtarjeta,
        idcuenta=data.idcuenta,
        idtipometodopago=data.idtipometodopago,
        activometodopagocuenta=data.activometodopagocuenta
    )

    db.add(metodo)
    db.commit()
    return {"mensaje": "Método de pago registrado correctamente"}