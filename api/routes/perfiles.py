from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
import random
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.ORM.models_sqlalchemy import Cuenta, Carrito, MetodoPagoCuenta
from api.DTO.models import CuentaCreate, LoginRequest,CuentaNombreCorreo, CorreoRequest, CuentaResponse, CuentaAdminUpdateRequest
from passlib.hash import bcrypt
import random
import string
import os
import uuid
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

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

def generar_token_corto(longitud=6):
    caracteres = string.ascii_uppercase + string.digits  # A-Z y 0-9
    return ''.join(random.choices(caracteres, k=longitud))

@router.post("/registrar2")
def registrar_cuenta2(cuenta_data: CuentaCreate, db: Session = Depends(get_db)):
    # Inicia la transacción
    try:
        # Generación del IDCUENTA con un formato único
        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        idcuenta = f"{random.randint(1, 9)}{now_str}"
        token_verificacion = generar_token_corto()
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
            DIRECCION=cuenta_data.direccion,
            TOKEN=token_verificacion  # <-- AQUÍ se guarda el token
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

        remitente = os.getenv("EMAIL_REMITENTE")
        contrasena = os.getenv("EMAIL_CONTRASENA")
        enlace = f"Aquí FELIEP ME PASA EL ENLACE"

        msg = EmailMessage()
        msg["Subject"] = "Verifica tu cuenta en ChibchaWeb"
        msg["From"] = formataddr(("ChibchaWeb", remitente))
        msg["To"] = cuenta_data.correo
        msg.set_content(
    f"""Hola {cuenta_data.nombrecuenta},

Gracias por registrarte en ChibchaWeb. Para activar tu cuenta, tienes dos opciones:

1. Haz clic en el siguiente enlace para verificar automáticamente:
   {enlace}

2. O bien, copia y pega este código en la página de verificación manual:
   Código de verificación: {token_verificacion}

Este código es válido por un tiempo limitado. Si no solicitaste este registro, puedes ignorar este mensaje.

Atentamente,
El equipo de ChibchaWeb
"""
)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remitente, contrasena)
            smtp.send_message(msg)

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
    cuentas = db.query(Cuenta).filter(Cuenta.IDTIPOCUENTA == idtipo).all()

    if not cuentas:
        raise HTTPException(status_code=404, detail="No se encontraron cuentas con ese tipo")

    # Solo extraemos los campos requeridos
    resultado = [{"nombrecuenta": c.NOMBRECUENTA, "correo": c.CORREO} for c in cuentas]

    return resultado

@router.post("/cuenta_por_correo", response_model=CuentaResponse)
def obtener_cuenta_por_correo(data: CorreoRequest, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter(Cuenta.CORREO == data.correo).first()
    
    if not cuenta:
        raise HTTPException(status_code=404, detail="No se encontró cuenta con ese correo.")
    
    return cuenta


@router.post("/solicitar-registro")
def solicitar_registro(nombre: str, correo: str, password: str, identificacion: str, telefono: str, db: Session = Depends(SessionLocal)):
    cuenta = db.query(Cuenta).filter(Cuenta.CORREO == correo).first()

    if cuenta:
        if cuenta.TOKEN == "NA":
            raise HTTPException(status_code=400, detail="El usuario ya está verificado.")
        else:
            token = cuenta.TOKEN  # Reutilizamos
    else:
        token = str(uuid.uuid4())
        nueva = Cuenta(
            IDCUENTA=str(uuid.uuid4())[:15],
            IDTIPOCUENTA=1,
            IDPAIS=170,
            PASSWORD=password,
            IDENTIFICACION=identificacion,
            NOMBRECUENTA=nombre,
            CORREO=correo,
            TELEFONO=telefono,
            FECHAREGISTRO=datetime.today(),
            DIRECCION="",
            TOKEN=token
        )
        db.add(nueva)
        db.commit()

    # ENVÍO DEL CORREO

    remitente = os.getenv("EMAIL_REMITENTE")
    contraseña = os.getenv("EMAIL_CONTRASENA") 

    msg = EmailMessage()
    msg["Subject"] = "Verificación de cuenta en ChibchaWeb"
    msg["From"] = formataddr(("ChibchaWeb", remitente))
    msg["To"] = correo

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remitente, contraseña)
        smtp.send_message(msg)
    return {"mensaje": "Correo enviado con verificación."}

@router.get("/confirmar-registro")
def confirmar_registro(token: str, idcuenta: str, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter(
        Cuenta.IDCUENTA == idcuenta,
        Cuenta.TOKEN == token
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Token inválido o IDCUENTA no coincide.")

    if cuenta.TOKEN == "NA":
        return {"mensaje": "Esta cuenta ya fue verificada."}

    cuenta.TOKEN = "NA"
    db.commit()

    return {"mensaje": "Cuenta verificada correctamente. Ya puedes iniciar sesión."}

@router.get("/estoy-verificado")
def estoy_verificado(idcuenta: str, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter(Cuenta.IDCUENTA == idcuenta).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")

    if cuenta.TOKEN == "NA":
        return {"verificado": True}
    else:
        return {"verificado": False}
    
@router.put("/admin/modificar_cuenta/{idcuenta}")
def modificar_cuenta_admin(idcuenta: str, datos_actualizados: CuentaAdminUpdateRequest, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter(Cuenta.IDCUENTA == idcuenta).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    campos_actualizables = [
        "IDTIPOCUENTA", "IDPAIS", "IDPLAN", "NOMBRECUENTA",
        "CORREO", "TELEFONO", "FECHAREGISTRO", "DIRECCION"
    ]

    for campo in campos_actualizables:
        nuevo_valor = getattr(datos_actualizados, campo.lower(), None)
        if nuevo_valor is not None:
            setattr(cuenta, campo, nuevo_valor)

    db.commit()
    db.refresh(cuenta)

    return {"mensaje": "Cuenta modificada correctamente"}
