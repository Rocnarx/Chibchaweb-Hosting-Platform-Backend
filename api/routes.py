from fastapi import APIRouter, Depends
from api.models import DomainRequest, DomainStatus, AlternativesResponse, PagoRequest, DominioPago
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from .database import SessionLocal
import requests
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
@router.post("/Dominios", response_model=AlternativesResponse)
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

# ✅ Endpoint de pagos (usando session de SQLAlchemy)
@router.post("/pagos")
def realizar_pago(pago: PagoRequest, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO factura (IDCUENTA, IDMETODOPAGO, IDCUENTAMETODOSPAGO, FECHAPAGO)
        VALUES (:idcuenta, :idmetodopago, :idcuentametodospago, :fecha)
    """), {
        "idcuenta": pago.idcuenta,
        "idmetodopago": pago.idmetodopago,
        "idcuentametodospago": pago.idcuentametodospago,
        "fecha": date.today()
    })

    result = db.execute(text("SELECT LAST_INSERT_ID() AS IDFACTURA"))
    idfactura = result.fetchone()[0]

    for d in pago.dominios:
    # Verificar si el dominio ya existe
        result = db.execute(text("SELECT 1 FROM dominio WHERE IDDOMINIO = :iddominio"), {"iddominio": d.iddominio})
        exists = result.fetchone()

    # Si no existe, insertarlo
        if not exists:
            nombre = d.iddominio.split('.')[0]
            db.execute(text("""
                INSERT INTO dominio (IDDOMINIO, NOMBREPAGINA, PRECIODOMINIO)
                VALUES (:iddominio, :nombre, :precio)
            """), {
                "iddominio": d.iddominio,
                "nombre": nombre,
                "precio": d.precio
            })

    # Insertar en facturadominio
    db.execute(text("""
        INSERT INTO facturadominio (IDFACTURA, IDDOMINIO, IDFACTURADOMINIO)
        VALUES (:idfactura, :iddominio, UUID())
    """), {"idfactura": idfactura, "iddominio": d.iddominio})
    
    db.commit()
    return {"message": "Pago realizado con éxito", "idfactura": idfactura}

@router.get("/perfil/{idcuenta}")
def obtener_tipo_usuario(idcuenta: str, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT t.NOMBRETIPO
        FROM cuenta c
        JOIN tipocuenta t ON c.IDTIPOCUENTA = t.IDTIPOCUENTA
        WHERE c.IDCUENTA = :id
    """), {"id": idcuenta}).fetchone()

    if result:
        return {"tipo": result[0]}
    else:
        return {"error": "Cuenta no encontrada"}

