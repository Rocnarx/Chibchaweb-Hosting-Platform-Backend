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
        .join(Cuenta.TIPOCUENTA)
        .filter(Cuenta.NOMBRECUENTA == nombrecuenta)
        .first()
    )

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    return RolUsuarioResponse(
        nombrecuenta=cuenta.NOMBRECUENTA,
        nombretipo=cuenta.TIPOCUENTA.NOMBRETIPO
    )

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
