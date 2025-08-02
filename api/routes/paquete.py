from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.DTO.models import CrearPaqueteRequest, PaqueteResponse, InfoPaqueteResponse, MiPaqueteResponse, ComprarPaqueteRequest
from api.DTO.models_sqlalchemy import InfoPaqueteHosting, PaqueteHosting, MetodoPagoCuenta, FacturaPaquete
from typing import List
from datetime import datetime, timedelta
import re
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

@router.get("/MiPaquete", response_model=MiPaqueteResponse)
def obtener_paquete_por_cuenta(idcuenta: str = Query(...), db: Session = Depends(get_db)):
    # Buscar método de pago asociado a la cuenta
    metodo = db.query(MetodoPagoCuenta).filter_by(IDCUENTA=idcuenta).first()
    if not metodo:
        raise HTTPException(status_code=404, detail="Método de pago no encontrado para la cuenta")

    # Buscar la factura asociada al método de pago
    factura = db.query(FacturaPaquete).filter_by(IDMETODOPAGOCUENTA=metodo.IDMETODOPAGOCUENTA).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura de paquete no encontrada")

    paquete = factura.paquete_hosting
    info = paquete.infopaquete

    return MiPaqueteResponse(
        idfacturapaquete=factura.IDFACTURAPAQUETE,
        fchpago=factura.FCHPAGO,
        fchvencimiento=factura.FCHVENCIMIENTO,
        estado=factura.ESTADO,
        valorfp=factura.VALORFP,
        preciopaquete=paquete.PRECIOPAQUETE,
        periodicidad=paquete.PERIODICIDAD,
        info=InfoPaqueteResponse(
            cantidadsitios=info.CANTIDADSITIOS,
            nombrepaquetehosting=info.NOMBREPAQUETEHOSTING,
            bd=info.BD,
            gbenssd=info.GBENSSD,
            correos=info.CORREOS,
            certificadosslhttps=info.CERTIFICADOSSSLHTTPS
        )
    )

@router.post("/ComprarPaquete")
def comprar_paquete(data: ComprarPaqueteRequest, db: Session = Depends(get_db)):
    try:
        # Paso 1: Obtener método de pago activo
        metodo = db.query(MetodoPagoCuenta).filter_by(IDCUENTA=data.idcuenta, ACTIVOMETODOPAGOCUENTA=True).first()
        if not metodo:
            raise HTTPException(status_code=404, detail="No se encontró método de pago activo para esta cuenta")

        # Paso 2: Verificar paquete
        paquete = db.query(PaqueteHosting).filter_by(IDPAQUETEHOSTING=data.idpaquetehosting).first()
        if not paquete:
            raise HTTPException(status_code=404, detail="Paquete no encontrado")

        # Paso 3: Calcular fechas
        hoy = datetime.now().date()

        # Extraer número de días desde el campo PERIODICIDAD (ej. "30 días", "90 días")
        match = re.search(r"(\d+)", paquete.PERIODICIDAD)
        if not match:
            raise HTTPException(status_code=400, detail="Periodicidad del paquete no válida")
        dias = int(match.group(1))
        vencimiento = hoy + timedelta(days=dias)

        # Paso 4: Crear factura
        nueva_factura = FacturaPaquete(
            IDMETODOPAGOCUENTA=metodo.IDMETODOPAGOCUENTA,
            IDPAQUETEHOSTING=paquete.IDPAQUETEHOSTING,
            FCHPAGO=hoy,
            FCHVENCIMIENTO=vencimiento,
            ESTADO=data.estado,
            VALORFP=paquete.PRECIOPAQUETE
        )

        db.add(nueva_factura)
        db.commit()
        db.refresh(nueva_factura)

        return {
            "message": "Paquete comprado exitosamente",
            "idfactura": nueva_factura.IDFACTURAPAQUETE,
            "fchpago": hoy.isoformat(),
            "fchvencimiento": vencimiento.isoformat()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))