from fastapi import APIRouter, Depends
from api.models import DomainRequest, DomainStatus, AlternativesResponse, PagoRequest, DominioPago
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from ..database import SessionLocal
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
