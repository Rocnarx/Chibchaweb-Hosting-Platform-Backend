from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from api.DAO.database import SessionLocal
from api.DTO.models import FacturaCreate, CarritoEstadoUpdate, ComisionUpdateRequest
from api.ORM.models_sqlalchemy import Factura, Carrito, Plan

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/realizarPago")
def realizar_pago(data: FacturaCreate, db: Session = Depends(get_db)):
    carrito = db.query(Carrito).filter_by(IDCARRITO=data.idcarrito).first()
    if not carrito:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    nueva_factura = Factura(
        IDCARRITO=data.idcarrito,
        PAGOFACTURA=datetime.now().date(),
        VIGFACTURA=(datetime.now() + timedelta(days=365*2)).date()
    )

    db.add(nueva_factura)
    db.commit()
    db.refresh(nueva_factura)

    return {
        "message": "Pago realizado con éxito",
        "idfactura": nueva_factura.IDFACTURA,
        "idcarrito": nueva_factura.IDCARRITO,
        "fecha_pago": nueva_factura.PAGOFACTURA,
        "vigencia_hasta": nueva_factura.VIGFACTURA
    }

@router.put("/confirmarPagoCarrito")
def confirmar_pago_carrito(data: CarritoEstadoUpdate, db: Session = Depends(get_db)):
    carrito = db.query(Carrito).filter_by(IDCARRITO=data.idcarrito).first()

    if not carrito:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    carrito.IDESTADOCARRITO = "2"  # Estado "facturado"
    db.commit()
    db.refresh(carrito)

    return {
        "message": "Estado del carrito actualizado a facturado",
        "idcarrito": carrito.IDCARRITO,
        "nuevo_estado": carrito.IDESTADOCARRITO
    }

@router.put("/modificar-comision")
def modificar_comision(data: ComisionUpdateRequest, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter_by(IDPLAN=data.idplan).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    plan.COMISION = data.comision
    plan.LIMITEDOMINIOS = data.limitedominios
    db.commit()
    db.refresh(plan)

    return {
        "message": f"Comisión actualizada correctamente para el plan {plan.NOMBREPLAN}",
        "idplan": plan.IDPLAN,
        "nueva_comision": plan.COMISION,
        "nuevo limite" : plan.LIMITEDOMINIOS
    }
