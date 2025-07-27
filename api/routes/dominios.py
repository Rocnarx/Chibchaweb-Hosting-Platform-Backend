from fastapi import APIRouter, Depends, HTTPException, Query
from api.models import DomainRequest, DomainStatus, AlternativesResponse, DominioCreate, DominioEnCarrito
from api.models_sqlalchemy import Dominio, CarritoDominio, Cuenta, MetodoPagoCuenta, Carrito
from sqlalchemy.orm import Session
from ..database import SessionLocal
import requests
from typing import List
from bs4 import BeautifulSoup

router = APIRouter()

HEADERS = { "User-Agent": "Mozilla/5.0" }
BASE_URL = "https://who.is/whois/"
EXTENSIONS = ["com", "net", "org", "co", "io", "app", "info", "dev", "online", "store"]

# Dependency para obtener una sesión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Web Scraping para WHOIS
def get_html(domain: str) -> str:
    url = BASE_URL + domain
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

def parse_data(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    result = {
        "registered": None,
        "expires": None
    }

    if "No WHOIS data was found for" in text:
        result["registered"] = False
        return result

    if "The domain" in text and "is registered" in text:
        result["registered"] = True

    expires_label = soup.find("dt", string="Expires")
    if expires_label:
        expires_value = expires_label.find_next_sibling("dd")
        if expires_value:
            result["expires"] = expires_value.text.strip()

    return result

# Endpoint WHOIS
@router.post("/DominiosDisponible", response_model=AlternativesResponse)
def verificar_extensiones(data: DomainRequest):
    base = data.domain.strip().lower()
    alternativas = []

    for ext in EXTENSIONS:
        dominio = f"{base}.{ext}"
        try:
            html = get_html(dominio)
            info = parse_data(html)
            alternativas.append(DomainStatus(
                domain=dominio,
                registered=info["registered"],
                expires=info["expires"]
            ))
        except:
            alternativas.append(DomainStatus(
                domain=dominio,
                registered=False,
                expires=None
            ))

    return AlternativesResponse(domain=base, alternativas=alternativas)

# Endpoint para agregar dominio a la base
@router.post("/agregarDominio")
def agregar_dominio(dominio_data: DominioCreate, db: Session = Depends(get_db)):
    if db.query(Dominio).filter_by(IDDOMINIO=dominio_data.iddominio).first():
        raise HTTPException(status_code=400, detail="ID de dominio ya registrado.")

    nuevo_dominio = Dominio(
        IDDOMINIO=dominio_data.iddominio,
        NOMBREPAGINA=dominio_data.nombrepagina,
        PRECIODOMINIO=dominio_data.preciodominio,
        OCUPADO=dominio_data.ocupado
    )

    db.add(nuevo_dominio)
    db.commit()
    db.refresh(nuevo_dominio)

    return {"message": "Dominio registrado exitosamente", "id": nuevo_dominio.IDDOMINIO}

@router.get("/carrito/dominios", response_model=List[DominioEnCarrito])
def obtener_dominios_facturados(idcuenta: str = Query(...), db: Session = Depends(get_db)):
    resultados = (
        db.query(
            Cuenta.IDCUENTA.label("cuenta"),
            Carrito.IDCARRITO.label("carrito"),
            Dominio.IDDOMINIO.label("iddominio"),
            Dominio.NOMBREPAGINA.label("dominio"),
            Dominio.PRECIODOMINIO.label("precio")
        )
        .join(MetodoPagoCuenta, MetodoPagoCuenta.IDCUENTA == Cuenta.IDCUENTA)
        .join(Carrito, Carrito.IDMETODOPAGOCUENTA == MetodoPagoCuenta.IDMETODOPAGOCUENTA)
        .join(CarritoDominio, CarritoDominio.IDCARRITO == Carrito.IDCARRITO)
        .join(Dominio, Dominio.IDDOMINIO == CarritoDominio.IDDOMINIO)
        .filter(Carrito.IDESTADOCARRITO == "2", Cuenta.IDCUENTA == idcuenta)
        .all()
    )

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron dominios para el carrito facturado")

    return resultados
