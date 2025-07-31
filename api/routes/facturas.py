from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.DTO.models_sqlalchemy import Carrito, Factura
from api.DTO.models import ObtenerFacturasRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/ObtenerFacturas")
def obtener_facturas(idcuenta: str, db: Session = Depends(get_db)):
    try:
        # Consultar todos los carritos asociados a la cuenta
        carritos = db.query(Carrito).filter_by(IDCUENTA=idcuenta).all()

        if not carritos:
            raise HTTPException(status_code=404, detail="No se encontraron carritos para esta cuenta")

        # Consultar las facturas asociadas a esos carritos
        facturas = db.query(Factura).filter(Factura.IDCARRITO.in_([carrito.IDCARRITO for carrito in carritos])).all()

        if not facturas:
            raise HTTPException(status_code=404, detail="No se encontraron facturas para esta cuenta")

        # Preparar el diccionario con las facturas
        facturas_dict = [
            {
                "idfactura": factura.IDFACTURA,
                "pago_factura": factura.PAGOFACTURA,
                "vig_factura": factura.VIGFACTURA
            }
            for factura in facturas
        ]

        return {"facturas": facturas_dict}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(e)}")
