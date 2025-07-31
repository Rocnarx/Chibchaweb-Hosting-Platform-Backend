from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import random
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.DTO.models_sqlalchemy import Cuenta, Carrito, MetodoPagoCuenta
from api.DTO.models import CuentaCreate, LoginRequest,CuentaNombreCorreo
from passlib.hash import bcrypt
from decimal import Decimal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

from sqlalchemy.exc import SQLAlchemyError

@router.post("/registrar2")
def registrar_cuenta2(cuenta_data: CuentaCreate, db: Session = Depends(get_db)):
    # Inicia la transacción
    try:
        # Generación del IDCUENTA con un formato único
        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        idcuenta = f"{random.randint(1, 9)}{now_str}"

        # Hashing de la contraseña
        hashed_password = bcrypt.hash(cuenta_data.password)

        # Creación de la cuenta en la base de datos
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

        # Insertamos la cuenta en la base de datos
        db.add(cuenta)
        db.commit()
        db.refresh(cuenta)

        # Crear el método de pago asociado al IDCUENTA
        metodo_pago = MetodoPagoCuenta(
            IDCUENTA=idcuenta,  # Ya no es necesario pasar IDMETODOPAGOCUENTA
            IDTIPOMETODOPAGO=1,  # ID para tarjeta de crédito
            ACTIVOMETODOPAGOCUENTA=True,  # Activamos el método de pago
        )

        db.add(metodo_pago)
        db.commit()
        db.refresh(metodo_pago)  # El ID se genera automáticamente

        # Crear un carrito asociado al IDCUENTA con el IDMETODOPAGOCUENTA correcto
        carrito = Carrito(
            IDESTADOCARRITO="1",  # Suponiendo que "1" es un estado válido
            IDCUENTA=idcuenta,
            IDMETODOPAGOCUENTA=metodo_pago.IDMETODOPAGOCUENTA  # Usamos el ID del método de pago recién creado
        )
        db.add(carrito)
        db.commit()
        db.refresh(carrito)

        # Devolvemos la respuesta con el IDCUENTA generado
        return {"message": "Cuenta, carrito y método de pago registrados exitosamente", "idcuenta": cuenta.IDCUENTA}
    
    except SQLAlchemyError as e:
        db.rollback()  # Si algo falla, deshacemos los cambios
        raise HTTPException(status_code=500, detail=f"Error al registrar: {str(e)}")

    except Exception as e:
        db.rollback()  # Deshacemos cualquier cambio si hay otro error
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
    
@router.get("/cuentas-por-tipo", response_model=List[CuentaNombreCorreo])
def obtener_cuentas_por_tipo(idtipo: int, db: Session = Depends(get_db)):
    id_decimal = Decimal(idtipo)  # 💡 Conversión clave
    cuentas = db.query(Cuenta).filter(Cuenta.IDTIPOCUENTA == idtipo).all()

    if not cuentas:
        raise HTTPException(status_code=404, detail="No se encontraron cuentas con ese tipo")

    # Solo extraemos los campos requeridos
    resultado = [{"nombrecuenta": c.NOMBRECUENTA, "correo": c.CORREO} for c in cuentas]

    return resultado

