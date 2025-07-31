from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from api.DAO.database import SessionLocal
from api.DTO.models_sqlalchemy import Cuenta, MetodoPagoCuenta, Tarjeta
from api.DTO.models import ListaMetodoPagoResponse, MetodoPagoUsuario

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/metodosPagoUsuario", response_model=ListaMetodoPagoResponse)
def obtener_metodos_pago_usuario(identificacion: str, db: Session = Depends(get_db)):
    cuenta = (
        db.query(Cuenta)
        .options(joinedload(Cuenta.METODOSPAGO).joinedload(MetodoPagoCuenta.TARJETA_REL))
        .filter(Cuenta.IDENTIFICACION == identificacion)
        .first()
    )

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")

    metodos = []
    for metodo in cuenta.METODOSPAGO:
        if metodo.TARJETA_REL:
            metodos.append(MetodoPagoUsuario(
                identificacion=cuenta.IDENTIFICACION,
                numerotarjeta=str(metodo.TARJETA_REL.NUMEROTARJETA),
                tipotarjeta=metodo.TARJETA_REL.IDTIPOTARJETA
            ))

    return ListaMetodoPagoResponse(metodos_pago=metodos)