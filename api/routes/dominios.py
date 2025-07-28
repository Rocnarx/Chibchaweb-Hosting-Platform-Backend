from fastapi import APIRouter, Depends, HTTPException, Query
from api.models import DomainRequest, DomainStatus, AlternativesResponse, DominioCreate, DominioEnCarrito, ActualizarOcupadoDominioRequest, AgregarDominioRequest
from api.models_sqlalchemy import Dominio, CarritoDominio, Cuenta, MetodoPagoCuenta, Carrito
from sqlalchemy.orm import Session
from ..database import SessionLocal
import requests
from typing import List
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, ElementTree
import smtplib
from email.message import EmailMessage
import os
from io import BytesIO
import uuid

router = APIRouter()


HEADERS = { "User-Agent": "Mozilla/5.0" }
BASE_URL = "https://who.is/whois/"
EXTENSIONS = ["com", "net", "org", "co", "io", "app", "info", "dev", "online", "store"]

def enviar_xml_por_correo(nombre_archivo: str, contenido_bytes: bytes):
    remitente = os.getenv("EMAIL_REMITENTE")
    password = os.getenv("EMAIL_CONTRASENA")
    destinatario = os.getenv("EMAIL_REMITENTE")

    msg = EmailMessage()
    msg["Subject"] = "Solicitud de Dominio CHIBCHAWEB"
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.set_content("Se adjunta la solicitud del dominio registrado. GRACIAS POR CONFIAR")

    msg.add_attachment(
        contenido_bytes,
        maintype="application",
        subtype="xml",
        filename=nombre_archivo
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(remitente, password)
        smtp.send_message(msg)


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

@router.put("/ActualizarOcupadoDominio")
def actualizar_ocupado_dominio(data: ActualizarOcupadoDominioRequest, db: Session = Depends(get_db)):
    dominio = db.query(Dominio).filter_by(IDDOMINIO=data.iddominio).first()
    if not dominio:
        raise HTTPException(status_code=404, detail="Dominio no encontrado")

    cuenta = db.query(Cuenta).filter_by(IDENTIFICACION=data.identificacion).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada para el dominio")

    dominio.OCUPADO = data.ocupado
    db.commit()
    db.refresh(dominio)

    mensaje = {"message": "Estado de dominio actualizado", "ocupado": dominio.OCUPADO}

    if dominio.OCUPADO:
        # Crear XML en memoria
        root = Element("SolicitudDominio")
        SubElement(root, "Identificacion").text = cuenta.IDENTIFICACION
        SubElement(root, "NombrePagina").text = dominio.NOMBREPAGINA
        SubElement(root, "PrecioDominio").text = str(dominio.PRECIODOMINIO)

        buffer = BytesIO()
        tree = ElementTree(root)
        tree.write(buffer, encoding="utf-8", xml_declaration=True)
        xml_bytes = buffer.getvalue()

        # Enviar XML por correo
        enviar_xml_por_correo(f"solicitud_{dominio.NOMBREPAGINA}.xml", xml_bytes)

        mensaje["correo"] = "Solicitud enviada por email"

    return mensaje

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
        .filter(
    Carrito.IDESTADOCARRITO.in_(["1", "2"]),
    Cuenta.IDCUENTA == idcuenta
)
        .all()
    )

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron dominios para el carrito facturado")

    return resultados

@router.post("/dominios/agregar-a-carrito-existente")
def agregar_dominio_a_carrito(data: AgregarDominioRequest, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter_by(IDCUENTA=data.idcuenta).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    dominio = db.query(Dominio).filter_by(IDDOMINIO=data.iddominio).first()
    if not dominio:
        raise HTTPException(status_code=404, detail="Dominio no encontrado")
    if dominio.OCUPADO:
        raise HTTPException(status_code=400, detail="Dominio ya está ocupado")

    carrito = db.query(Carrito).filter_by(IDCUENTA=data.idcuenta, IDESTADOCARRITO='1').first()
    if not carrito:
        raise HTTPException(status_code=404, detail="No hay carrito activo para esta cuenta")


    ya_existe = db.query(CarritoDominio).filter_by(IDDOMINIO=data.iddominio, IDCARRITO=carrito.IDCARRITO).first()
    if ya_existe:
        raise HTTPException(status_code=400, detail="Este dominio ya está en el carrito")

    nuevo_item = CarritoDominio(
        IDDOMINIO=data.iddominio,
        IDCARRITO=carrito.IDCARRITO
    )
    db.add(nuevo_item)
    db.commit()

    return {
        "message": "Dominio agregado exitosamente al carrito activo",
        "idcarrito": carrito.IDCARRITO,
        "iddominio": data.iddominio
    }