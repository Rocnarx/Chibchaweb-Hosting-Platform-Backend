from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api.models import MetodoPagoCuentaCreate, TarjetaCreate
from api.models_sqlalchemy import MetodoPagoCuenta, Tarjeta
from cryptography.fernet import Fernet

key = Fernet.generate_key()  
cipher = Fernet(key)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tarjeta")
def registrar_tarjeta(tarjeta_data: TarjetaCreate, db: Session = Depends(get_db)):
    try:
        # Encrypt sensitive data
        encrypted_numero_tarjeta = cipher.encrypt(tarjeta_data.numerotarjeta.encode())
        encrypted_ccv = cipher.encrypt(tarjeta_data.ccv.encode())

        nueva_tarjeta = Tarjeta(
            IDTIPOTARJETA=tarjeta_data.idtipotarjeta,
            NUMEROTARJETA=encrypted_numero_tarjeta,
            CCV=encrypted_ccv,
            FECHAVTO=tarjeta_data.fechavto
        )

        db.add(nueva_tarjeta)
        db.commit()
        db.refresh(nueva_tarjeta)  # Obtener el ID autogenerado

        return {
            "mensaje": "Tarjeta registrada correctamente",
            "idtarjeta": nueva_tarjeta.IDTARJETA
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar la tarjeta: {e}")


@router.post("/metodopago")
def agregar_metodo_pago(data: MetodoPagoCuentaCreate, db: Session = Depends(get_db)):
    metodo = MetodoPagoCuenta(
        IDTARJETA=data.idtarjeta,
        IDCUENTA=data.idcuenta,
        IDTIPOMETODOPAGO=data.idtipometodopago,
        ACTIVOMETODOPAGOCUENTA=data.activometodopagocuenta
    )

    db.add(metodo)
    db.commit()
    return {"mensaje": "Método de pago registrado correctamente"}




@router.post("/validarTarjeta")
def validar_tarjeta(idtarjeta: str, ccv: str, db: Session = Depends(get_db)):
    try:
        # Obtener la tarjeta desde la base de datos
        tarjeta = db.query(Tarjeta).filter(Tarjeta.IDTARJETA == idtarjeta).first()

        # Si la tarjeta no existe
        if not tarjeta:
            raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

        # Desencriptar el CCV almacenado
        decrypted_ccv = cipher.decrypt(tarjeta.CCV).decode()

        # Comparar el CCV proporcionado con el almacenado
        if decrypted_ccv == ccv:
            return {"valid": True}
        else:
            return {"valid": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar la tarjeta: {e}")