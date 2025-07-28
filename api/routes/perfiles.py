from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import random
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api.models_sqlalchemy import Cuenta
from api.models import RolUsuarioResponse, CuentaCreate, LoginRequest
from passlib.hash import bcrypt

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/registrar")
def registrar_cuenta(cuenta_data: CuentaCreate, db: Session = Depends(get_db)):
    now_str = datetime.now().strftime("%Y%m%d%H%M%S")
    idcuenta = f"{random.randint(1, 9)}{now_str}"

    hashed_password = bcrypt.hash(cuenta_data.password)

    cuenta = Cuenta(
        IDCUENTA=idcuenta,
        IDTIPOCUENTA=cuenta_data.idtipocuenta,
        IDPAIS=cuenta_data.idpais,
        IDPLAN=cuenta_data.idplan,
        PASSWORD=hashed_password,
        IDENTIFICACION=cuenta_data.identificacion,
        NOMBRECUENTA=cuenta_data.nombrecuenta,
        CORREO=cuenta_data.correo,
        TELEFONO=cuenta_data.telefono,
        FECHAREGISTRO=datetime.now().date(),
        DIRECCION=cuenta_data.direccion
    )

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)

    return {"message": "Cuenta registrada exitosamente", "idcuenta": cuenta.IDCUENTA}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    cuenta = (
        db.query(Cuenta)
        .filter(Cuenta.IDENTIFICACION == data.identificacion)
        .first()
    )

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    if not bcrypt.verify(data.password, cuenta.PASSWORD):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {
        "message": "Inicio de sesión exitoso",
        "idcuenta": cuenta.IDCUENTA,
        "nombrecuenta": cuenta.NOMBRECUENTA,
        "identificacion": cuenta.IDENTIFICACION,
        "tipocuenta": cuenta.TIPOCUENTA_REL.NOMBRETIPO if cuenta.TIPOCUENTA_REL else None,
        "pais": cuenta.PAIS_REL.NOMBREPAIS if cuenta.PAIS_REL else None,
        "plan": cuenta.PLAN_REL.NOMBREPLAN if cuenta.PLAN_REL else None,
        "correo": cuenta.CORREO,
        "telefono": cuenta.TELEFONO,
        "fecharegistro": cuenta.FECHAREGISTRO.isoformat(),
        "direccion": cuenta.DIRECCION
    }