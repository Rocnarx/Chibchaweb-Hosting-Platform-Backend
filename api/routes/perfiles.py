from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import random
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api.models_sqlalchemy import Cuenta
from api.models import RolUsuarioResponse, CuentaCreate
from passlib.hash import bcrypt

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/usuario/rol", response_model=RolUsuarioResponse)
def obtener_rol_usuario(nombrecuenta: str, db: Session = Depends(get_db)):
    cuenta = (
        db.query(Cuenta)
        .join(Cuenta.tipocuenta)
        .filter(Cuenta.nombrecuenta == nombrecuenta)
        .first()
    )

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    return RolUsuarioResponse(
        nombrecuenta=cuenta.nombrecuenta,
        nombretipo=cuenta.tipocuenta.nombretipo
    )

@router.post("/registrar")
def registrar_cuenta(cuenta_data: CuentaCreate, db: Session = Depends(get_db)):
    now_str = datetime.now().strftime("%Y%m%d%H%M%S")
    idcuenta = f"{random.randint(1, 9)}{now_str}"

    hashed_password = bcrypt.hash(cuenta_data.password)

    cuenta = Cuenta(
        idcuenta=idcuenta,
        idtipocuenta=cuenta_data.idtipocuenta,
        idpais=cuenta_data.idpais,
        idplan=cuenta_data.idplan,
        password=hashed_password,
        identificacion=cuenta_data.identificacion,
        nombrecuenta=cuenta_data.nombrecuenta,
        correo=cuenta_data.correo,
        telefono=cuenta_data.telefono,
        fecharegistro=datetime.now().date(),
        direccion=cuenta_data.direccion
    )

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)

    return {"message": "Cuenta registrada exitosamente", "idcuenta": cuenta.idcuenta}